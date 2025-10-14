from __future__ import annotations

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text
from .base import BaseMapping, MappingResult

__all__ = ["LinuxMapping", "mapping"]


class LinuxMapping(BaseMapping):
    name = "linux"

    def map(self, event: ParsedEvent) -> MappingResult:
        severity = priority_to_severity(event.priority)
        fields = event.fields
        signature = sanitize_text(fields.get("event_id", fields.get("AUDIT_ID", "linux")))
        message = sanitize_text(event.message)
        name = sanitize_text(fields.get("event", event.app_name or "Linux Event"))
        extensions: dict[str, str] = {
            "msg": message,
            "cs1Label": "rawEvent",
            "cs1": sanitize_text(fields.get("raw", event.raw)),
            "deviceHostName": sanitize_text(event.host or ""),
            "deviceProcessName": sanitize_text(event.app_name or ""),
        }
        auth_keys = {"user": "suser", "uid": "suid", "auid": "cs2", "exe": "cs3"}
        for source_key, cef_key in auth_keys.items():
            if source_key in fields:
                extensions[cef_key] = sanitize_text(fields[source_key])
        return MappingResult(
            signature_id=signature,
            name=name,
            severity=severity,
            extensions=extensions,
        )


mapping = LinuxMapping()
