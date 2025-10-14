from __future__ import annotations

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text
from .base import BaseMapping, MappingResult

__all__ = ["DefaultMapping", "mapping"]


class DefaultMapping(BaseMapping):
    name = "default"

    def map(self, event: ParsedEvent) -> MappingResult:
        severity = priority_to_severity(event.priority)
        signature = _coalesce(event.fields, ["event_id", "eventId", "eventid", "msgid"], "generic")
        name = sanitize_text(event.fields.get("event", event.message)) or "Generic Event"
        extensions: dict[str, str] = {
            "msg": sanitize_text(event.message),
            "deviceHostName": sanitize_text(event.host or ""),
            "deviceProcessName": sanitize_text(event.app_name or ""),
        }
        for key, value in event.fields.items():
            extensions[key] = sanitize_text(value)
        return MappingResult(
            signature_id=signature,
            name=name,
            severity=severity,
            extensions=extensions,
        )


def _coalesce(fields: dict[str, object], keys: list[str], default: str) -> str:
    for key in keys:
        value = fields.get(key)
        if value:
            return sanitize_text(value)
    return default


mapping = DefaultMapping()
