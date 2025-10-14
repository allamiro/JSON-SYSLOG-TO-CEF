from __future__ import annotations

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text
from .base import BaseMapping, MappingResult

__all__ = ["CiscoMapping", "mapping"]


class CiscoMapping(BaseMapping):
    name = "cisco"

    def map(self, event: ParsedEvent) -> MappingResult:
        fields = event.fields
        signature = sanitize_text(fields.get("message_id", fields.get("event_id", "cisco")))
        message = sanitize_text(fields.get("msg", event.message))
        name = sanitize_text(fields.get("event", message)) or "Cisco Event"
        severity = _severity_from_message(message, event.priority)
        extensions: dict[str, str] = {
            "deviceHostName": sanitize_text(event.host or ""),
            "deviceProcessName": sanitize_text(event.app_name or ""),
            "msg": message,
        }
        for key in ("src", "dst", "src_ip", "dst_ip", "spt", "dpt", "sport", "dport", "proto"):
            if key in fields:
                normalized_key = _NORMALIZED_KEYS.get(key, key)
                extensions[normalized_key] = sanitize_text(fields[key])
        if "action" in fields:
            extensions["act"] = sanitize_text(fields["action"])
        return MappingResult(
            signature_id=signature,
            name=name,
            severity=severity,
            extensions=extensions,
        )


def _severity_from_message(message: str, priority: int | None) -> int:
    lowered = message.lower()
    if any(token in lowered for token in ["deny", "blocked", "teardown"]):
        return 8
    if "allow" in lowered or "permitted" in lowered:
        return 3
    return priority_to_severity(priority)


_NORMALIZED_KEYS = {
    "src_ip": "src",
    "dst_ip": "dst",
    "sport": "spt",
    "dport": "dpt",
}


mapping = CiscoMapping()
