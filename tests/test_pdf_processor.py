from app.pdf_processor import extract_text
import pytest

def test_text_extraction():
    # Create a sample PDF (or use a test file)
    text = extract_text("data/sample1.pdf")
    assert isinstance(text, str)
    assert len(text) > 0

def test_invalid_pdf():
    with pytest.raises(RuntimeError):
        extract_text("invalid_file.pdf")