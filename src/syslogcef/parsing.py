from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, tzinfo

from ._datetime import smart_parse
from .utils import ParsedEvent, ensure_tz, sanitize_text

__all__ = ["ParsedSyslog", "parse_syslog", "parse_kv_pairs"]

RFC5424_RE = re.compile(
    r"^<(?P<pri>\d+)>(?P<version>\d+)\s+"
    r"(?P<timestamp>\S+)\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<appname>\S+)\s+"
    r"(?P<procid>\S+)\s+"
    r"(?P<msgid>\S+)\s+"
    r"(?P<structured>(?:-|(?:\[[^\]]*\])+))\s*"
    r"(?P<msg>.*)$"
)

RFC3164_RE = re.compile(
    r"^<(?P<pri>\d+)>(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<tag>[\w\-./]+)(?:\[(?P<pid>[^\]]+)\])?:\s*(?P<msg>.*)$"
)

KV_RE = re.compile(r"(?P<key>[\w./-]+)=(?P<value>\".*?\"|\S+)")
JSON_FRAGMENT_RE = re.compile(r"\{.*\}")


@dataclass(slots=True)
class ParsedSyslog:
    pri: int | None
    version: int | None
    timestamp: datetime | None
    hostname: str | None
    app_name: str | None
    procid: str | None
    msgid: str | None
    message: str
    structured_data: dict[str, dict[str, str]]
    kv_pairs: dict[str, str]
    raw: str

    def as_event(self, default_tz: tzinfo | None = None) -> ParsedEvent:
        ts = ensure_tz(self.timestamp, default_tz)
        return ParsedEvent(
            timestamp=ts,
            host=self.hostname,
            app_name=self.app_name,
            priority=self.pri,
            message=self.message,
            fields={**flatten_structured_data(self.structured_data), **self.kv_pairs},
            raw={
                "pri": self.pri,
                "version": self.version,
                "timestamp": ts.isoformat() if ts else None,
                "hostname": self.hostname,
                "app_name": self.app_name,
                "procid": self.procid,
                "msgid": self.msgid,
                "message": self.message,
                "structured_data": self.structured_data,
            },
            source=self.app_name,
        )


def flatten_structured_data(data: dict[str, dict[str, str]]) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for sd_id, kv in data.items():
        for key, value in kv.items():
            flattened[f"{sd_id}.{key}"] = value
    return flattened


def _parse_timestamp(text: str) -> datetime | None:
    return smart_parse(text)


def _parse_structured_data(text: str) -> dict[str, dict[str, str]]:
    if text == "-" or not text:
        return {}
    result: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"\[(?P<id>[^\s\]=]+)(?P<data>[^\]]*)\]", text):
        sd_id = match.group("id")
        data_text = match.group("data")
        sd_dict: dict[str, str] = {}
        for kv_match in re.finditer(r"(?P<key>[\w\-.]+)=\"(?P<value>.*?)\"", data_text):
            sd_dict[kv_match.group("key")] = kv_match.group("value")
        result[sd_id] = sd_dict
    return result


def parse_kv_pairs(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for match in KV_RE.finditer(text):
        value = match.group("value")
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        pairs[match.group("key")] = value
    if not pairs:
        json_match = JSON_FRAGMENT_RE.search(text)
        if json_match:
            fragment = json_match.group(0)
            try:
                data = json.loads(fragment)
                for key, value in data.items():
                    pairs[key] = sanitize_text(value)
            except (json.JSONDecodeError, AttributeError):
                pairs["raw_json"] = fragment
    return pairs


def parse_syslog(line: str, *, default_tz: tzinfo | None = None) -> ParsedSyslog:
    raw_line = line.rstrip("\n")
    match = RFC5424_RE.match(raw_line)
    if match:
        pri = int(match.group("pri"))
        version = int(match.group("version"))
        timestamp = _parse_timestamp(match.group("timestamp"))
        hostname = _normalize_value(match.group("hostname"))
        appname = _normalize_value(match.group("appname"))
        procid = _normalize_optional(match.group("procid"))
        msgid = _normalize_optional(match.group("msgid"))
        structured_data = _parse_structured_data(match.group("structured"))
        msg = match.group("msg")
        kv_pairs = parse_kv_pairs(msg)
        return ParsedSyslog(
            pri=pri,
            version=version,
            timestamp=ensure_tz(timestamp, default_tz),
            hostname=hostname,
            app_name=appname,
            procid=procid,
            msgid=msgid,
            message=msg,
            structured_data=structured_data,
            kv_pairs=kv_pairs,
            raw=raw_line,
        )

    match = RFC3164_RE.match(raw_line)
    pri = version = None
    timestamp = hostname = appname = procid = msgid = None
    structured_data: dict[str, dict[str, str]] = {}
    kv_pairs: dict[str, str] = {}
    message = raw_line
    if match:
        pri = int(match.group("pri"))
        timestamp = _parse_timestamp(match.group("timestamp"))
        hostname = match.group("hostname")
        appname = match.group("tag")
        procid = match.group("pid")
        message = match.group("msg")
        kv_pairs = parse_kv_pairs(message)
    else:
        kv_pairs = parse_kv_pairs(raw_line)
    return ParsedSyslog(
        pri=pri,
        version=version,
        timestamp=ensure_tz(timestamp, default_tz),
        hostname=hostname,
        app_name=appname,
        procid=procid,
        msgid=msgid,
        message=message,
        structured_data=structured_data,
        kv_pairs=kv_pairs,
        raw=raw_line,
    )


def _normalize_value(value: str) -> str:
    if value == "-":
        return ""
    return value


def _normalize_optional(value: str) -> str | None:
    if value == "-":
        return None
    return value
