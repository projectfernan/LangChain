from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from app.api.upload import router as upload_router

app = FastAPI(title="LangChain Chat API", root_path="/api")

# Add CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(rag_router)
