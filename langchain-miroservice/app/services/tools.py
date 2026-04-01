import math
import os
from datetime import datetime, timezone
from pathlib import Path
from langchain_core.tools import tool
from duckduckgo_search import DDGS

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"
ALLOWED_EXTENSIONS = {".txt", ".csv", ".json", ".md", ".py", ".pdf"}
MAX_FILE_SIZE_BYTES = 50_000        # ~50KB for text files
MAX_PDF_FILE_SIZE_BYTES = 10_000_000  # ~10MB for PDFs


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Input must be a valid Python math
    expression string, e.g. '2 + 2', 'sqrt(16)', '3 * (4 + 5)'.
    Supported functions: sqrt, sin, cos, tan, log, log10, pi, e."""
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed["abs"] = abs
    allowed["round"] = round
    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


@tool
def read_file(filename: str) -> str:
    """Read the contents of a file from the uploads folder.
    Use this when the user mentions a filename or asks you to read, summarize,
    or answer questions about a file. Input should be just the filename
    (e.g. 'notes.txt', 'report.pdf'), not the full path.
    Supported formats: .txt, .csv, .json, .md, .py, .pdf"""
    try:
        file_path = (UPLOADS_DIR / filename).resolve()

        if not str(file_path).startswith(str(UPLOADS_DIR)):
            return "Access denied: file is outside the uploads folder."

        if not file_path.exists():
            return f"File '{filename}' not found in the uploads folder."

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return (
                f"Unsupported file type '{file_path.suffix}'. "
                f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        is_pdf = file_path.suffix.lower() == ".pdf"
        size_limit = MAX_PDF_FILE_SIZE_BYTES if is_pdf else MAX_FILE_SIZE_BYTES
        size_label = "10MB" if is_pdf else "50KB"

        if file_path.stat().st_size > size_limit:
            return f"File is too large to read (max {size_label} for {file_path.suffix} files)."

        # PDF: extract text from all pages
        if file_path.suffix.lower() == ".pdf":
            import pdfplumber
            extracted = []
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted.append(text)
            if extracted:
                return "\n\n".join(extracted)
            return (
                "No text could be extracted from this PDF. "
                "It may be a scanned/image-based PDF. "
                "Please provide a text-based PDF for best results."
            )

        return file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error reading file: {exc}"


@tool
def search_web(query: str) -> str:
    """Search the web for current information using DuckDuckGo.
    Use this when the user asks about recent events, news, people, places,
    or anything that may not be in the model's training data.
    Input should be a clear search query string."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found."
        formatted = []
        for r in results:
            formatted.append(
                f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}"
            )
        return "\n\n".join(formatted)
    except Exception as exc:
        return f"Search failed: {exc}"


@tool
def get_current_datetime(timezone_name: str = "UTC") -> str:
    """Return the current date and time. Pass timezone_name as an IANA timezone
    string (e.g. 'America/New_York', 'Europe/London'). Defaults to UTC."""
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(timezone_name)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")
