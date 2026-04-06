from typing import AsyncGenerator

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages,
)
from langgraph.prebuilt import create_react_agent

from app.core.config import (
    SUMMARY_PROMPT,
    SUMMARY_TOKEN_THRESHOLD,
    get_model,
    get_summarizer_model,
)
from app.services.tools import calculator, get_current_datetime, read_file, search_web

_model = get_model()
_summarizer = get_summarizer_model()

TOOLS = [calculator, get_current_datetime, search_web, read_file]

_agent = create_react_agent(
    model=_model,
    tools=TOOLS,
    prompt=(
        "You are a helpful assistant. You have access to the following tools:\n"
        "- calculator: for arithmetic and math expressions\n"
        "- get_current_datetime: for the current date and time\n"
        "- search_web: for recent news, events, or anything outside your training data\n"
        "- read_file: for reading files from the uploads folder\n\n"
        "Important rules:\n"
        "- Always prefer tool results over guessing.\n"
        "- When using search_web, summarize the results clearly and concisely.\n"
        "- When using read_file, answer the user's question based on the file content."
    ),
)

# Per-session state #
# NOTE: In-memory only — lost on restart, not safe for multiple workers. #
_session_histories: dict[str, list] = {}


def _get_history(session_id: str) -> list:
    if session_id not in _session_histories:
        _session_histories[session_id] = []
    return _session_histories[session_id]


def _maybe_summarize(session_id: str) -> None:
    """Summarize old messages when history exceeds the token threshold.

    Keeps the last 4 messages verbatim and replaces everything before them
    with a single SystemMessage summary. This mirrors ConversationSummaryBufferMemory
    without using the deprecated API.
    """
    history = _get_history(session_id)
    if len(history) < 6:
        return

    trimmed = trim_messages(
        history,
        max_tokens=SUMMARY_TOKEN_THRESHOLD,
        token_counter="approximate",
        strategy="last",
        start_on="human",
        include_system=True,
    )

    if len(trimmed) == len(history):
        return  # Still within budget

    to_summarize = history[: len(history) - len(trimmed)]
    if not to_summarize:
        return

    lines = []
    for msg in to_summarize:
        if isinstance(msg, HumanMessage):
            lines.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage) and isinstance(msg.content, str):
            lines.append(f"Assistant: {msg.content}")

    if not lines:
        return

    transcript = "\n".join(lines)
    summary_chain = SUMMARY_PROMPT | _summarizer
    summary_result = summary_chain.invoke({"conversation": transcript})
    summary_text = (
        summary_result.content
        if hasattr(summary_result, "content")
        else str(summary_result)
    )

    _session_histories[session_id] = [
        SystemMessage(content=f"[Conversation summary so far]: {summary_text}"),
        *trimmed,
    ]

def get_chat_reply(session_id: str, user_message: str) -> str:
    """Synchronous single-turn chat. Returns the final assistant reply."""
    _maybe_summarize(session_id)
    history = _get_history(session_id)

    result = _agent.invoke({"messages": history + [HumanMessage(content=user_message)]})

    all_messages = result["messages"]
    reply = all_messages[-1].content

    _session_histories[session_id] = list(all_messages)
    return reply


async def stream_chat_reply(session_id: str, user_message: str) -> AsyncGenerator[str, None]:
    """Async generator that yields text chunks for SSE streaming."""
    _maybe_summarize(session_id)
    history = _get_history(session_id)
    input_messages = history + [HumanMessage(content=user_message)]

    accumulated_messages = list(input_messages)

    async for event in _agent.astream_events(
        {"messages": input_messages},
        version="v2",
    ):
        kind = event.get("event")

        if kind == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and isinstance(chunk.content, str):
                text = chunk.content
                if text:
                    yield text

        elif kind == "on_tool_start":
            tool_name = event.get("name", "tool")
            yield f"\n[Using tool: {tool_name}...]\n"

        elif kind == "on_chain_end" and event.get("name") == "LangGraph":
            output = event.get("data", {}).get("output", {})
            if "messages" in output:
                accumulated_messages = list(output["messages"])

    _session_histories[session_id] = accumulated_messages
