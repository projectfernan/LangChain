from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import get_model
from app.services.tools import UPLOADS_DIR



_embeddings = OpenAIEmbeddings()
_model = get_model()

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

_rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant. The user has uploaded a document. "
        "The following context contains extracted content from that document. "
        "Answer the user's question based on this context. "
        "If asked about the file or document, describe what you found in the context. "
        "Do not say there is no file — the context below IS the file content.\n\n"
        "Context:\n{context}"
    ),
    ("human", "{question}"),
])


# In-memory vector store per document — keyed by filename
_vector_stores: dict[str, FAISS] = {}

def ingest_document(filename: str) -> int:
    """
    Load a file from the uploads folder, split it into chunks,
    embed them and store in a FAISS index.
    Returns the number of chunks created.
    """
    file_path = UPLOADS_DIR / filename

    if file_path.suffix.lower() == ".pdf":
        import pdfplumber
        documents = []
        with pdfplumber.open(str(file_path)) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    documents.append(Document(
                        page_content=text,
                        metadata={"source": filename, "page": i + 1}
                    ))
        if not documents:
            raise ValueError(
                f"No text could be extracted from '{filename}'. "
                "It may be a scanned/image-based PDF."
            )
    else:
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents = loader.load()

    chunks = _splitter.split_documents(documents)

    _vector_stores[filename] = FAISS.from_documents(chunks, _embeddings)
    return len(chunks)


def rag_chat(filename: str, question: str) -> dict:
    """
    Retrieve the most relevant chunks for the question and
    return the AI answer plus the source snippets used.
    """
    if filename not in _vector_stores:
        raise ValueError(
            f"'{filename}' has not been ingested. Please upload it via POST /rag/upload first."
        )

    vector_store = _vector_stores[filename]
    relevant_docs = vector_store.similarity_search(question, k=3)

    context = "\n\n".join(doc.page_content for doc in relevant_docs)
    sources = [doc.page_content[:150] + "..." for doc in relevant_docs]

    chain = _rag_prompt | _model
    result = chain.invoke({"context": context, "question": question})

    return {
        "reply": result.content,
        "sources": sources,
    }
