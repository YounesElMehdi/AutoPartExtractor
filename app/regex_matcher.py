import re

def find_part_numbers(text: str) -> list:
    """Extracts part numbers using regex."""
    pattern = r'\b(?:[A-Z]*\d+[A-Z0-9]*|E\d+)(?:_[A-Z]{3})?\b'
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return list(set(matches))  # Remove duplicates