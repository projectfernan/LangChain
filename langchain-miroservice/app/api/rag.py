from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.chat_models import RagUploadResponse, RagChatRequest, RagChatResponse
from app.services.tools import UPLOADS_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_PDF_FILE_SIZE_BYTES
from app.services.rag_service import ingest_document, rag_chat

router = APIRouter(prefix="/rag")


@router.post("/upload", response_model=RagUploadResponse)
async def rag_upload(file: UploadFile = File(...)):
    try:
        suffix = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        contents = await file.read()
        is_pdf = suffix == ".pdf"
        size_limit = MAX_PDF_FILE_SIZE_BYTES if is_pdf else MAX_FILE_SIZE_BYTES
        size_label = "10MB" if is_pdf else "50KB"

        if len(contents) > size_limit:
            raise HTTPException(
                status_code=400,
                detail=f"File is too large (max {size_label} for {suffix} files)."
            )

        # Save to uploads folder
        dest = UPLOADS_DIR / file.filename
        dest.write_bytes(contents)

        # Chunk + embed + store
        chunks = ingest_document(file.filename)

        return RagUploadResponse(
            filename=file.filename,
            chunks=chunks,
            message=f"'{file.filename}' ingested into {chunks} chunks. You can now chat with it via POST /rag/chat."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=RagChatResponse)
def rag_chat_endpoint(req: RagChatRequest):
    try:
        result = rag_chat(req.filename, req.message)
        return RagChatResponse(reply=result["reply"], sources=result["sources"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
