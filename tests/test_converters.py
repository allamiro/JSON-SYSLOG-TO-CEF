from __future__ import annotations

import json
from pathlib import Path

from syslogcef.converters import convert_line, from_json, parse_syslog, to_cef
from syslogcef.mappings import get_mapping

DATA_DIR = Path(__file__).parent / "data"


def test_convert_line_syslog_sample():
    with (DATA_DIR / "cisco-ios.log").open(encoding="utf-8") as handle:
        line = handle.readline()
    cef = convert_line(line, source="cisco")
    assert cef.startswith("CEF:0")
    assert "deviceVendor" in cef


def test_from_json_sample():
    data = json.loads((DATA_DIR / "cisco-ios.json").read_text(encoding="utf-8"))
    event = from_json(data[0])
    mapping = get_mapping("cisco")
    cef = to_cef(event, "Vendor", "Product", "1.0", mapping)
    assert "CEF:" in cef
    assert "msg=" in cef


def test_convert_line_parse_error():
    line = "{invalid json"
    cef = convert_line(line, source="default")
    assert "flexString1=parse_error" in cef


def test_to_cef_includes_timestamp():
    parsed = parse_syslog("<134>1 2023-02-01T12:34:56Z host app 1 - - hi")
    event = parsed.as_event()
    mapping = get_mapping("default")
    cef = to_cef(event, "Vendor", "Product", "1.0", mapping)
    assert "end=2023-02-01T12:34:56+00:00" in cef
