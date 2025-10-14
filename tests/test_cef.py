from __future__ import annotations

from syslogcef.cef import CEFHeader, build_cef, escape_cef_header, priority_to_severity


def test_escape_cef_header():
    assert escape_cef_header("vendor|name=1\\") == r"vendor\|name\=1\\\\"


def test_build_cef_with_extensions():
    header = CEFHeader(
        device_vendor="Vendor",
        device_product="Product",
        device_version="1.0",
        signature_id="100",
        name="Test",
        severity=5,
    )
    cef = build_cef(header, {"msg": "hello", "src": "1.2.3.4"})
    assert cef.startswith("CEF:0|Vendor|Product|1.0|100|Test|5 ")
    assert "msg=hello" in cef
    assert "src=1.2.3.4" in cef


def test_priority_to_severity_bounds():
    for priority in range(0, 192):
        sev = priority_to_severity(priority)
        assert 0 <= sev <= 10
