from __future__ import annotations

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text
from .base import BaseMapping, MappingResult

__all__ = ["VMwareMapping", "mapping"]


class VMwareMapping(BaseMapping):
    name = "vmware"

    def map(self, event: ParsedEvent) -> MappingResult:
        fields = event.fields
        signature = sanitize_text(fields.get("event_id", fields.get("eventTypeId", "vmware")))
        name = sanitize_text(fields.get("event", fields.get("eventType", "VMware Event")))
        severity = priority_to_severity(event.priority)
        message = sanitize_text(event.message)
        extensions: dict[str, str] = {
            "msg": message,
            "deviceHostName": sanitize_text(event.host or ""),
            "deviceProcessName": sanitize_text(event.app_name or ""),
        }
        if "user" in fields:
            extensions["suser"] = sanitize_text(fields["user"])
        if "vm" in fields:
            extensions["destinationServiceName"] = sanitize_text(fields["vm"])
        if "ip" in fields:
            extensions["src"] = sanitize_text(fields["ip"])
        return MappingResult(
            signature_id=signature,
            name=name,
            severity=severity,
            extensions=extensions,
        )


mapping = VMwareMapping()
