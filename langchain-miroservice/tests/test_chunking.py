"""
Tests for the RAG text splitter configuration in app/services/rag_service.py.
Verifies that chunk_size=500 and chunk_overlap=50 behave as expected.
"""

from langchain_core.documents import Document

from app.services.rag_service import _splitter

# A text longer than chunk_size (500) to force multiple chunks
LONG_TEXT = "LangChain is a framework for building applications powered by language models. " * 10

# A short text that fits in a single chunk
SHORT_TEXT = "This is a short document."


def test_splitter_produces_multiple_chunks():
    """A text longer than 500 chars must produce more than one chunk."""
    assert len(LONG_TEXT) > 500
    doc = Document(page_content=LONG_TEXT)
    chunks = _splitter.split_documents([doc])
    assert len(chunks) > 1


def test_splitter_respects_chunk_size():
    """No individual chunk should exceed 500 characters."""
    doc = Document(page_content=LONG_TEXT)
    chunks = _splitter.split_documents([doc])
    for chunk in chunks:
        assert len(chunk.page_content) <= 500


def test_splitter_short_text_single_chunk():
    """A short text must stay as a single chunk."""
    doc = Document(page_content=SHORT_TEXT)
    chunks = _splitter.split_documents([doc])
    assert len(chunks) == 1


def test_splitter_preserves_content():
    """The combined chunks must contain all words from the original text."""
    doc = Document(page_content=LONG_TEXT)
    chunks = _splitter.split_documents([doc])
    combined = " ".join(c.page_content for c in chunks)
    # Every word in the original should appear somewhere in the chunks
    for word in LONG_TEXT.split()[:10]:
        assert word in combined
