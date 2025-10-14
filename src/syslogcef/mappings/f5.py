from __future__ import annotations

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text
from .base import BaseMapping, MappingResult

__all__ = ["F5Mapping", "mapping"]


class F5Mapping(BaseMapping):
    name = "f5"

    def map(self, event: ParsedEvent) -> MappingResult:
        fields = event.fields
        signature = sanitize_text(fields.get("event_id", "f5"))
        name = sanitize_text(fields.get("irule", fields.get("event", "F5 Event")))
        severity = priority_to_severity(event.priority)
        message = sanitize_text(event.message)
        extensions: dict[str, str] = {
            "msg": message,
            "deviceHostName": sanitize_text(event.host or ""),
            "deviceProcessName": sanitize_text(event.app_name or ""),
        }
        for key in ("client_ip", "client_port", "server_ip", "server_port", "vip"):
            if key in fields:
                extensions[_KEY_MAP.get(key, key)] = sanitize_text(fields[key])
        if "request" in fields:
            extensions["request"] = sanitize_text(fields["request"])
        return MappingResult(
            signature_id=signature,
            name=name,
            severity=severity,
            extensions=extensions,
        )


_KEY_MAP = {
    "client_ip": "src",
    "client_port": "spt",
    "server_ip": "dst",
    "server_port": "dpt",
}


mapping = F5Mapping()
