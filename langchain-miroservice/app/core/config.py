import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

# Number of tokens in history before old messages get summarized
SUMMARY_TOKEN_THRESHOLD = int(os.getenv("SUMMARY_TOKEN_THRESHOLD", "1000"))


def get_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        temperature=0.7,
    )


def get_summarizer_model() -> ChatOpenAI:
    """Lower-temperature model used only for producing conversation summaries."""
    return ChatOpenAI(
        model=os.getenv("SUMMARIZER_MODEL_NAME", "gpt-3.5-turbo"),
        temperature=0.0,
    )


SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "human",
        "Distill the following conversation into a single concise paragraph that "
        "preserves all key facts, decisions and context. Write in third person.\n\n"
        "Conversation:\n{conversation}\n\nSummary:"
    )
])
