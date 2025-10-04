import json
from typing import Any, List

_PARSE_FAILED = object()


def remove_json_prefix_list(content: str) -> Any:
    if isinstance(content, str):
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
        try:
            decoded = json.loads(content)
            return decoded
        except Exception:
            return _PARSE_FAILED
    elif isinstance(content, list):
        return content
    else:
        return _PARSE_FAILED
