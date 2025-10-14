from __future__ import annotations

from datetime import datetime
from typing import Optional

try:  # pragma: no cover - optional dependency
    from dateutil import parser as date_parser
except ImportError:  # pragma: no cover - fallback path tested separately
    date_parser = None


COMMON_FORMATS = [
    "%b %d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]


def smart_parse(text: str) -> Optional[datetime]:
    if not text or text == "-":
        return None
    if date_parser is not None:
        try:
            return date_parser.parse(text)
        except (ValueError, TypeError):
            return None
    cleaned = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        pass
    for fmt in COMMON_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None
