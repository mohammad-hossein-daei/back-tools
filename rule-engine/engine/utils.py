import json
from typing import Any


def load_json_file(filepath: str) -> Any:
    """بارگذاری فایل JSON و برگرداندن محتوای آن"""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading {filepath}: {e}")