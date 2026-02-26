# engine/utils.py

import json
from typing import Any, Dict, List

def load_json_file(filepath: str) -> Any:
    """بارگذاری فایل JSON و برگردوندن محتوای اون"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)