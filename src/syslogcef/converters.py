from __future__ import annotations

import json
from datetime import datetime, tzinfo
from typing import Any, Iterable, Mapping

from .cef import CEFHeader, build_cef
from .mappings import get_mapping
from .mappings.base import Mapping
from .parsing import ParsedSyslog, parse_syslog as _parse_syslog
from .utils import ParsedEvent, ensure_tz, sanitize_text
from ._datetime import smart_parse

__all__ = ["convert_line", "parse_syslog", "from_json", "to_cef"]


DEFAULT_VENDOR = "JSON-SYSLOG"
DEFAULT_PRODUCT = "syslogcef"
DEFAULT_VERSION = "0.1.0"


def parse_syslog(line: str, *, default_tz: tzinfo | None = None) -> ParsedSyslog:
    return _parse_syslog(line, default_tz=default_tz)


def from_json(event: Mapping[str, Any], *, default_tz: tzinfo | None = None) -> ParsedEvent:
    timestamp = _parse_timestamp(event)
    if timestamp:
        timestamp = ensure_tz(timestamp, default_tz)
    host = _coalesce(event, ["host", "hostname", "deviceHostName"])
    app = _coalesce(event, ["app", "appname", "process", "program"])
    priority = None
    if "priority" in event:
        try:
            priority = int(event["priority"])
        except (TypeError, ValueError):
            priority = None
    message = sanitize_text(event.get("message") or event.get("msg") or json.dumps(event))
    fields = {key: value for key, value in event.items() if value is not None}
    return ParsedEvent(
        timestamp=timestamp,
        host=host,
        app_name=app,
        priority=priority,
        message=message,
        fields={k: sanitize_text(v) for k, v in fields.items()},
        raw=event,
        source=app or host,
    )


def _parse_timestamp(event: Mapping[str, Any]) -> datetime | None:
    for key in ("timestamp", "time", "@timestamp", "eventTime"):
        value = event.get(key)
        if not value:
            continue
        parsed = smart_parse(str(value))
        if parsed is not None:
            return parsed
    return None


def _coalesce(data: Mapping[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = data.get(key)
        if value:
            return sanitize_text(value)
    return None


def to_cef(
    event: ParsedEvent,
    vendor: str,
    product: str,
    version: str,
    mapping: Mapping,
) -> str:
    mapping_result = mapping.map(event)
    severity = max(0, min(mapping_result.severity, 10))
    header = CEFHeader(
        device_vendor=vendor,
        device_product=product,
        device_version=version,
        signature_id=mapping_result.signature_id,
        name=mapping_result.name,
        severity=severity,
    )
    extensions = {
        "deviceVendor": vendor,
        "deviceProduct": product,
        "deviceVersion": version,
    }
    if event.timestamp:
        extensions["end"] = event.timestamp.isoformat()
    if event.host:
        extensions["deviceHostName"] = event.host
    if event.app_name:
        extensions["deviceProcessName"] = event.app_name
    if event.priority is not None:
        extensions["syslogSeverity"] = str(event.priority % 8)
    extensions.update(mapping_result.extensions)
    return build_cef(header, extensions)


def convert_line(
    line: str,
    source: str | None = None,
    mapping: Mapping | None = None,
    *,
    vendor: str = DEFAULT_VENDOR,
    product: str = DEFAULT_PRODUCT,
    version: str = DEFAULT_VERSION,
    default_tz: tzinfo | None = None,
    strict: bool = False,
) -> str:
    try:
        parsed_event = _parse_line_to_event(line, default_tz=default_tz)
        mapping_obj = mapping or get_mapping(source)
        return to_cef(parsed_event, vendor, product, version, mapping_obj)
    except Exception as exc:
        if strict:
            raise
        fallback_event = ParsedEvent(
            timestamp=None,
            host=None,
            app_name=None,
            priority=None,
            message=line.strip(),
            fields={"flexString1": "parse_error", "cs1Label": "error", "cs1": sanitize_text(str(exc))},
            raw=None,
            source=source,
        )
        mapping_obj = mapping or get_mapping("default")
        return to_cef(fallback_event, vendor, product, version, mapping_obj)


def _parse_line_to_event(
    line: str,
    *,
    default_tz: tzinfo | None,
) -> ParsedEvent:
    trimmed = line.strip()
    if trimmed.startswith("{"):
        data = json.loads(trimmed)
        if not isinstance(data, Mapping):
            raise ValueError("JSON log line must be an object")
        return from_json(data, default_tz=default_tz)
    syslog = parse_syslog(line, default_tz=default_tz)
    return syslog.as_event()
