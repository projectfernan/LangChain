"""
Tests for file validation constants defined in app/services/tools.py.
Verifies allowed extensions and size limits used by upload endpoints.
"""

from app.services.tools import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_PDF_FILE_SIZE_BYTES

# - Allowed extensions -

def test_txt_is_allowed():
    assert ".txt" in ALLOWED_EXTENSIONS


def test_pdf_is_allowed():
    assert ".pdf" in ALLOWED_EXTENSIONS


def test_csv_is_allowed():
    assert ".csv" in ALLOWED_EXTENSIONS


def test_json_is_allowed():
    assert ".json" in ALLOWED_EXTENSIONS


def test_md_is_allowed():
    assert ".md" in ALLOWED_EXTENSIONS


def test_py_is_allowed():
    assert ".py" in ALLOWED_EXTENSIONS


def test_exe_is_not_allowed():
    assert ".exe" not in ALLOWED_EXTENSIONS


def test_bat_is_not_allowed():
    assert ".bat" not in ALLOWED_EXTENSIONS


def test_js_is_not_allowed():
    assert ".js" not in ALLOWED_EXTENSIONS


# - Size limits -

def test_text_size_limit_is_50kb():
    assert MAX_FILE_SIZE_BYTES == 50_000


def test_pdf_size_limit_is_10mb():
    assert MAX_PDF_FILE_SIZE_BYTES == 10_000_000


def test_pdf_limit_is_larger_than_text_limit():
    """PDFs get a higher size limit than plain text files."""
    assert MAX_PDF_FILE_SIZE_BYTES > MAX_FILE_SIZE_BYTES
