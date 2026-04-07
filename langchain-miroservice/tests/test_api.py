"""
Tests for FastAPI endpoints using TestClient.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ─ POST /chat -

def test_chat_endpoint_returns_200(mocker):
    mocker.patch("app.api.chat.get_chat_reply", return_value="mocked reply")
    response = client.post(
        "/chat",
        json={"session_id": "test-session", "message": "hello"},
    )
    assert response.status_code == 200
    assert response.json() == {"reply": "mocked reply"}


def test_chat_endpoint_missing_fields():
    """Missing required fields must return 422 Unprocessable Entity."""
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_chat_endpoint_missing_message():
    response = client.post("/chat", json={"session_id": "test-session"})
    assert response.status_code == 422


def test_chat_endpoint_empty_message_is_accepted(mocker):
    """The API accepts empty strings — validation is the model's concern."""
    mocker.patch("app.api.chat.get_chat_reply", return_value="mocked reply")
    response = client.post(
        "/chat",
        json={"session_id": "test-session", "message": ""},
    )
    assert response.status_code == 200

def test_chat_stream_endpoint_returns_200(mocker):
    """Stream endpoint must return 200 with text/event-stream content type."""
    async def mock_stream(*args, **kwargs):
        yield "Hello"
        yield " world"

    mocker.patch("app.api.chat.stream_chat_reply", side_effect=mock_stream)
    response = client.post(
        "/chat/stream",
        json={"session_id": "test-session", "message": "hello"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

# ─ POST /chat stream -

def test_chat_stream_endpoint_sse_format(mocker):
    """Each chunk must be prefixed with 'data: ' and stream ends with [DONE]."""
    async def mock_stream(*args, **kwargs):
        yield "Hello"
        yield " world"

    mocker.patch("app.api.chat.stream_chat_reply", side_effect=mock_stream)
    response = client.post(
        "/chat/stream",
        json={"session_id": "test-session", "message": "hello"},
    )
    assert "data: Hello" in response.text
    assert "data:  world" in response.text
    assert "data: [DONE]" in response.text


def test_chat_stream_endpoint_missing_fields():
    """Missing required fields must return 422."""
    response = client.post("/chat/stream", json={})
    assert response.status_code == 422

# ─ POST /rag/upload ─

def test_rag_upload_invalid_extension():
    """Uploading a disallowed file type must return 400."""
    response = client.post(
        "/rag/upload",
        files={"file": ("malware.exe", b"fake content", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_rag_upload_no_file():
    """Missing file field must return 422."""
    response = client.post("/rag/upload")
    assert response.status_code == 422


# ─ POST /upload-and-chat ─

def test_upload_and_chat_valid_file(mocker):
    """Valid file + session_id must return 200 with filename and reply."""
    mocker.patch("app.api.upload._save_file")
    mocker.patch("app.api.upload.get_chat_reply", return_value="Here is a summary.")
    response = client.post(
        "/upload-and-chat",
        data={"session_id": "test-session"},
        files={"file": ("notes.txt", b"Some text content", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "notes.txt"
    assert response.json()["reply"] == "Here is a summary."


def test_upload_and_chat_invalid_extension():
    """Disallowed file type must return 400."""
    response = client.post(
        "/upload-and-chat",
        data={"session_id": "test-session"},
        files={"file": ("virus.exe", b"bad content", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_and_chat_file_too_large():
    """File exceeding the size limit must return 400."""
    response = client.post(
        "/upload-and-chat",
        data={"session_id": "test-session"},
        files={"file": ("big.txt", b"x" * 50_001, "text/plain")},
    )
    assert response.status_code == 400


def test_upload_and_chat_missing_session_id():
    """Missing session_id form field must return 422."""
    response = client.post(
        "/upload-and-chat",
        files={"file": ("notes.txt", b"content", "text/plain")},
    )
    assert response.status_code == 422


def test_upload_and_chat_missing_file():
    """Missing file field must return 422."""
    response = client.post(
        "/upload-and-chat",
        data={"session_id": "test-session"},
    )
    assert response.status_code == 422


# ─ POST /rag/chat -

def test_rag_chat_filename_not_found():
    """Chatting with a filename that was never uploaded must return 404."""
    response = client.post(
        "/rag/chat",
        json={
            "session_id": "test-session",
            "filename": "nonexistent_file.txt",
            "message": "what is this?",
        },
    )
    assert response.status_code == 404


def test_rag_chat_missing_fields():
    """Missing required fields must return 422."""
    response = client.post("/rag/chat", json={})
    assert response.status_code == 422
