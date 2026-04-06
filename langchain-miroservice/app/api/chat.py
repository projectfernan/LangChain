import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.chat_models import ChatRequest, ChatResponse, StreamRequest
from app.services.chat_service import get_chat_reply, stream_chat_reply

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        reply = get_chat_reply(req.session_id, req.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream_endpoint(req: StreamRequest):
    """
    Server-Sent Events endpoint. Streams the response token by token.

    Each chunk format:  data: <text>\n\n
    End of stream:      data: [DONE]\n\n
    Error format:       data: [ERROR] <message>\n\n

    JavaScript example:
        const res = await fetch('/chat/stream', { method: 'POST', body: ... });
        const reader = res.body.getReader();
        // read chunks until [DONE]
    """
    async def event_generator():
        try:
            async for chunk in stream_chat_reply(req.session_id, req.message):
                # Escape newlines to keep SSE framing valid
                safe_chunk = chunk.replace("\n", "\\n")
                yield f"data: {safe_chunk}\n\n"
        except asyncio.CancelledError:
            return  # Client disconnected
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
            return
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Prevents Nginx from buffering the stream
            "Connection": "keep-alive",
        },
    )
