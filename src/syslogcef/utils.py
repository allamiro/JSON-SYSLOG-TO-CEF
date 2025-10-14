from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone, tzinfo
from typing import Any


@dataclass(slots=True)
class ParsedEvent:
    """Representation of a normalized event ready for CEF encoding."""

    timestamp: datetime | None
    host: str | None
    app_name: str | None
    priority: int | None
    message: str
    fields: dict[str, Any] = field(default_factory=dict)
    raw: Mapping[str, Any] | None = None
    source: str | None = None

    def copy_with_fields(self, **extra: Any) -> ParsedEvent:
        combined = dict(self.fields)
        combined.update(extra)
        return ParsedEvent(
            timestamp=self.timestamp,
            host=self.host,
            app_name=self.app_name,
            priority=self.priority,
            message=self.message,
            fields=combined,
            raw=self.raw,
            source=self.source,
        )


def sanitize_text(value: Any) -> str:
    """Return a UTF-8 safe string."""

    if value is None:
        return ""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = str(value)
    return text.replace("\u0000", "?")


def safe_int(value: Any) -> int | None:
    try:
        if isinstance(value, bool) or value is None:
            return None
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def safe_float(value: Any) -> float | None:
    try:
        if isinstance(value, bool) or value is None:
            return None
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def ensure_tz(dt: datetime | None, default_tz: tzinfo | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        if default_tz is not None:
            return dt.replace(tzinfo=default_tz)
        return dt.replace(tzinfo=timezone.utc)
    return dt


__all__ = [
    "ParsedEvent",
    "sanitize_text",
    "safe_int",
    "safe_float",
    "ensure_tz",
]
