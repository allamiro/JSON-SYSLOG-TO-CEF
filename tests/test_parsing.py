from __future__ import annotations

from datetime import timezone

from syslogcef.parsing import parse_kv_pairs, parse_syslog


def test_parse_rfc3164_line():
    line = "<189>Feb  8 04:00:48 host app[123]: user=alice action=login"
    parsed = parse_syslog(line)
    assert parsed.pri == 189
    assert parsed.hostname == "host"
    assert parsed.app_name == "app"
    assert parsed.kv_pairs["user"] == "alice"
    assert parsed.kv_pairs["action"] == "login"


def test_parse_rfc5424_line():
    line = '<134>1 2023-02-01T12:34:56Z host app 1234 - [exampleSDID@32473 foo="bar"] message'
    parsed = parse_syslog(line)
    assert parsed.version == 1
    assert parsed.structured_data["exampleSDID@32473"]["foo"] == "bar"
    assert parsed.message == "message"


def test_parse_syslog_timezone():
    line = "<134>1 2023-02-01T12:34:56 host app 1234 - - test"
    parsed = parse_syslog(line, default_tz=timezone.utc)
    assert parsed.timestamp.tzinfo == timezone.utc


def test_parse_kv_pairs_with_json_fragment():
    fragment = 'msg {"user":"bob","action":"logout"}'
    kv = parse_kv_pairs(fragment)
    assert kv["user"] == "bob"
    assert kv["action"] == "logout"
