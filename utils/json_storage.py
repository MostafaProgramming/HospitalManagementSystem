import json
from pathlib import Path


# All JSON files are stored relative to the project folder.
BASE_DIR = Path(__file__).resolve().parent.parent


def resolve_path(filename):
    # Allow the app to work with either absolute paths or project-relative paths.
    path = Path(filename)
    if path.is_absolute():
        return path
    return BASE_DIR / path


def load_data(filename, default=None):
    # Load a JSON file. If it does not exist yet, create it with default data.
    if default is None:
        default = {}

    path = resolve_path(filename)

    if not path.exists():
        save_data(filename, default)
        return default.copy() if isinstance(default, dict) else list(default)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default.copy() if isinstance(default, dict) else list(default)


def save_data(filename, data):
    # Save Python data back into a JSON file with readable indentation.
    path = resolve_path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
