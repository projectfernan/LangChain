"""
Tests for calculator, get_current_datetime, read_file, and search_web tools.
"""

from app.services.tools import calculator, get_current_datetime, read_file, search_web


# ─ calculator ─

def test_calculator_addition():
    assert calculator.func("2 + 2") == "4"


def test_calculator_sqrt():
    assert calculator.func("sqrt(16)") == "4.0"


def test_calculator_division():
    assert calculator.func("10 / 2") == "5.0"


def test_calculator_multiplication():
    assert calculator.func("3 * 7") == "21"


def test_calculator_invalid_expression():
    """Blocked expressions must return an error string, not raise."""
    result = calculator.func("os.system('x')")
    assert isinstance(result, str)
    assert result.startswith("Error")


def test_calculator_syntax_error():
    result = calculator.func("2 +* 3")
    assert isinstance(result, str)
    assert result.startswith("Error")


# ─ get_current_datetime ─

def test_get_current_datetime_utc():
    result = get_current_datetime.func("UTC")
    assert isinstance(result, str)
    assert "UTC" in result


def test_get_current_datetime_returns_string():
    result = get_current_datetime.func("UTC")
    # Format: "YYYY-MM-DD HH:MM:SS TZ"
    assert len(result) > 10


def test_get_current_datetime_manila():
    result = get_current_datetime.func("Asia/Manila")
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_current_datetime_invalid_timezone():
    """Invalid timezone should fall back to UTC without raising."""
    result = get_current_datetime.func("Invalid/Timezone")
    assert isinstance(result, str)
    assert len(result) > 0


# ─ read_file ─

def test_read_file_path_traversal():
    """Path traversal attempt must be blocked."""
    result = read_file.func("../secret.txt")
    assert "Access denied" in result


def test_read_file_not_found():
    """Missing file must return a not-found message, not raise."""
    result = read_file.func("nonexistent_xyz_12345.txt")
    assert "not found" in result


def test_read_file_unsupported_type(tmp_path, mocker):
    """Files with disallowed extensions must be rejected."""
    mocker.patch("app.services.tools.UPLOADS_DIR", tmp_path)
    (tmp_path / "virus.exe").write_bytes(b"fake")
    result = read_file.func("virus.exe")
    assert "Unsupported" in result


def test_read_file_reads_text_content(tmp_path, mocker):
    """Valid .txt file must return its contents."""
    mocker.patch("app.services.tools.UPLOADS_DIR", tmp_path)
    (tmp_path / "hello.txt").write_text("hello world", encoding="utf-8")
    result = read_file.func("hello.txt")
    assert result == "hello world"


def test_read_file_too_large(tmp_path, mocker):
    """File exceeding the size limit must return an error string, not raise."""
    mocker.patch("app.services.tools.UPLOADS_DIR", tmp_path)
    (tmp_path / "big.txt").write_bytes(b"x" * 50_001)
    result = read_file.func("big.txt")
    assert "too large" in result


# ─ search_web ─

def test_search_web_returns_formatted_results(mocker):
    """Valid search must return title, URL, and summary."""
    mock_results = [
        {"title": "Test Title", "href": "https://google.com", "body": "Test summary"}
    ]
    mocker.patch("app.services.tools.DDGS").return_value.__enter__.return_value.text.return_value = mock_results
    result = search_web.func("test query")
    assert "Test Title" in result
    assert "https://google.com" in result
    assert "Test summary" in result


def test_search_web_no_results(mocker):
    """Empty search results must return a clear message."""
    mocker.patch("app.services.tools.DDGS").return_value.__enter__.return_value.text.return_value = []
    result = search_web.func("obscure query with no results")
    assert result == "No results found."


def test_search_web_network_failure(mocker):
    """Network errors must be caught and returned as a string, not raised."""
    mocker.patch("app.services.tools.DDGS", side_effect=Exception("network error"))
    result = search_web.func("any query")
    assert result.startswith("Search failed:")
