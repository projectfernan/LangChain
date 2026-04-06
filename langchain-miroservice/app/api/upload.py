from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.chat_models import UploadChatResponse
from app.services.chat_service import get_chat_reply
from app.services.tools import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_BYTES,
    MAX_PDF_FILE_SIZE_BYTES,
    UPLOADS_DIR,
)

router = APIRouter()


def _save_file(file_contents: bytes, filename: str) -> None:
    """Validate and save uploaded file contents to the uploads folder."""
    suffix = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    is_pdf = suffix == ".pdf"
    size_limit = MAX_PDF_FILE_SIZE_BYTES if is_pdf else MAX_FILE_SIZE_BYTES
    size_label = "10MB" if is_pdf else "50KB"

    if len(file_contents) > size_limit:
        raise HTTPException(
            status_code=400,
            detail=f"File is too large (max {size_label} for {suffix} files)."
        )
    dest = UPLOADS_DIR / filename
    dest.write_bytes(file_contents)


@router.post("/upload-and-chat", response_model=UploadChatResponse)
async def upload_and_chat(
    file: UploadFile = File(...),
    session_id: str = Form(...),
    message: str = Form("Summarize this file for me.")
):
    try:
        contents = await file.read()
        _save_file(contents, file.filename)

        # Inject filename into the message so the agent knows what to read
        full_message = f"{message} The file is: {file.filename}"
        reply = get_chat_reply(session_id, full_message)

        return UploadChatResponse(filename=file.filename, reply=reply)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
