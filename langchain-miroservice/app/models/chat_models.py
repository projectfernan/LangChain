from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


class StreamRequest(BaseModel):
    session_id: str
    message: str


class UploadChatResponse(BaseModel):
    filename: str
    reply: str


class RagUploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class RagChatRequest(BaseModel):
    session_id: str
    filename: str
    message: str


class RagChatResponse(BaseModel):
    reply: str
    sources: list[str]
