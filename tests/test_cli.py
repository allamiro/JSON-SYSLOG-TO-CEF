from __future__ import annotations

import io
import json

from syslogcef import cli


def test_cli_json_input(capsys, monkeypatch):
    data = json.dumps({"message": "hello", "host": "example"}) + "\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(data))
    exit_code = cli.main(["--format", "json", "--source", "default", "--stats"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "CEF:" in captured.out
    assert "processed=1" in captured.err


def test_cli_mapping_override(tmp_path, capsys, monkeypatch):
    mapping_file = tmp_path / "mapping.json"
    with mapping_file.open("w", encoding="utf-8") as handle:
        json.dump({"cs2Label": "custom"}, handle)
    monkeypatch.setattr("sys.stdin", io.StringIO("not syslog\n"))
    exit_code = cli.main(
        [
            "--source",
            "default",
            "--mapping-file",
            str(mapping_file),
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "cs2Label=custom" in captured.out
