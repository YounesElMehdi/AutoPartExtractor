from pathlib import Path  # Add this import
import fitz

def extract_text_to_file(pdf_path: str, output_file: Path) -> None:
    """Extracts text from PDF and saves to a file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)