import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def resolve_path(filename):
    path = Path(filename)
    if path.is_absolute():
        return path
    return BASE_DIR / path


def load_data(filename, default=None):
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
    path = resolve_path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
