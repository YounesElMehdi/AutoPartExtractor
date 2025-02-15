import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.gui import main

if __name__ == "__main__":
    main()