import json
import re
import shutil
from pathlib import Path  # Ensure this is imported
from datetime import datetime
from Levenshtein import distance

def load_config() -> dict:
    """Load configuration from settings.json."""
    config_path = Path("app/config/settings.json")
    with open(config_path, "r") as f:
        return json.load(f)

def save_config(config: dict) -> None:
    """Save configuration to settings.json."""
    config_path = Path("app/config/settings.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def get_whitelist_path() -> str:
    """Get whitelist path from config."""
    return load_config().get("whitelist_path", "app/ValidatedWhitelist.txt")

def create_operation_folder(pdf_path: str) -> Path:
    """Creates a dated folder for the operation."""
    pdf_name = Path(pdf_path).stem.replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{pdf_name}"
    operation_folder = Path("app/operations") / folder_name
    
    if operation_folder.exists():
        shutil.rmtree(operation_folder)
    operation_folder.mkdir(parents=True)
    return operation_folder

def save_to_file(data: list, file_path: Path) -> None:
    """Saves data to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(data))

def load_whitelist() -> set:
    """Loads validated part numbers from the whitelist."""
    whitelist_path = Path(get_whitelist_path())
    with open(whitelist_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f}

def simple_regex_extractor(text: str) -> list:
    """Extract part numbers using configurable regex."""
    config = load_config()
    pattern = config["regex_pattern"]
    return list(set(re.findall(pattern, text)))

def levenshtein_similarity(candidate: str, whitelist: set) -> list:
    """Find similar part numbers using configurable threshold."""
    config = load_config()
    max_distance = config["similarity_threshold"]
    similar = []
    for pn in whitelist:
        if distance(candidate, pn) <= max_distance:
            similar.append(pn)
    return similar