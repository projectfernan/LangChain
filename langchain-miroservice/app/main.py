from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.rag import router as rag_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LangChain Chat API")

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