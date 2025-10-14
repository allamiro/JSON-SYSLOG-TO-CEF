# syslogcef

![CI](https://github.com/allamiro/JSON-SYSLOG-TO-CEF/actions/workflows/ci.yml/badge.svg)
![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

`syslogcef` converts RFC3164/RFC5424 syslog lines and structured JSON events into ArcSight CEF. The
package ships with deterministic vendor mappings, a streaming CLI, and a composable Python API so
the same conversion logic can be reused in collectors, enrichment services, and offline pipelines.

Key capabilities:

- Deterministic mapping of common syslog/JSON fields into valid CEF headers and extensions.
- RFC3164/RFC5424 parsing with key/value extraction, UTF-8 sanitation, and timezone awareness.
- High-throughput CLI featuring tail mode, worker pools, streaming I/O, and statistics reporting.
- Extensible mapping registry for Cisco, Linux, F5, VMware, and site-specific overrides.

![Architecture](images/jsoncef.png)

## Table of contents

1. [Installation](#installation)
2. [Quickstart](#quickstart)
3. [CLI usage](#cli-usage)
4. [Library usage](#library-usage)
5. [Mapping architecture](#mapping-architecture)
6. [Error handling](#error-handling)
7. [Performance and benchmarking](#performance-and-benchmarking)
8. [Sample data & rsyslog templates](#sample-data--rsyslog-templates)
9. [Development workflow](#development-workflow)
10. [Contributing](#contributing)
11. [License](#license)

## Installation

The package requires **Python 3.10+**. Install the latest release from the repository root:

```bash
pip install .
```

Install with development tooling:

```bash
pip install .[dev]
```

Optional extras:

- `python-dateutil` enables rich timezone parsing (automatically detected when installed).
- `PyYAML` enables `--mapping-file` overrides that use YAML syntax.

For isolated CLI use consider [`pipx`](https://pypa.github.io/pipx/):

```bash
pipx install "syslogcef @ git+https://github.com/allamiro/JSON-SYSLOG-TO-CEF"
```

## Quickstart

Convert a syslog file into CEF using the Cisco mapping:

```bash
syslogcef --input syslog-logs/cisco/cisco-ios.log --source cisco
```

Stream JSON events from stdin, emit CEF to stdout, and collect processing statistics:

```bash
cat json-logs/cisco/cisco-ios.json \
  | syslogcef --format json --source linux --stats
```

Tail `/var/log/messages` and append CEF events to a file:

```bash
syslogcef --input /var/log/messages --output /tmp/messages.cef --watch --source linux
```

## CLI usage

`syslogcef` processes newline-delimited input without buffering entire files. Run `syslogcef --help`
to inspect every option. Highlights include:

| Flag | Description |
| --- | --- |
| `--input PATH` / `-` | Read from a file or stdin. |
| `--output PATH` / `-` | Write to a file or stdout. |
| `--format {syslog,json}` | Force input format instead of auto-detection. |
| `--vendor/--product/--version` | Override CEF device fields when using custom mappings. |
| `--source {default,cisco,linux,f5,vmware}` | Choose a built-in mapping. |
| `--mapping-file PATH` | Load an additional JSON/YAML mapping definition. |
| `--watch` | Tail the input file for continuous ingestion. |
| `--workers N` | Enable a worker pool for CPU-bound conversions. |
| `--tz Europe/Berlin` | Apply a default timezone to naive timestamps. |
| `--strict` | Exit non-zero on parse failures instead of emitting error-tagged CEF. |
| `--stats` | Print processed/failed counters to stderr on exit. |

CLI logging is structured and suitable for parsing by downstream observability tooling. When
`--strict` is omitted, malformed lines are converted into CEF with `flexString1Label=error` so they
remain visible in ArcSight while being easy to filter.

## Library usage

Use the public API to embed the converter:

```python
import json

from syslogcef import convert_line, from_json, parse_syslog, to_cef
from syslogcef.mappings import get_mapping

syslog_line = "<189>Feb  8 04:00:48 host sshd[123]: user=alice action=login"
parsed_syslog = parse_syslog(syslog_line)
event = parsed_syslog.as_event()

linux_mapping = get_mapping("linux")
cef_line = to_cef(event, vendor="Example", product="Collector", version="1.0", mapping=linux_mapping)

json_event = {"message": "Login", "host": "firewall", "action": "allow"}
cef_from_json = convert_line(json.dumps(json_event), source="linux")
```

Dataclasses exposed by the package:

- `ParsedSyslog`: structured representation of RFC3164/5424 lines with facility/severity helpers.
- `ParsedEvent`: normalised event with message, timestamps, priority, and arbitrary extensions.

The mapping protocol returns `(signature_id, name, severity, extension_dict)` and is implemented by
modules under `syslogcef.mappings`. Custom mappings can subclass `MappingBase` or supply a callable
matching the protocol signature.

## Mapping architecture

Built-in mappings translate raw events into consistent ArcSight fields:

- `default`: preserves message, host, process, and timestamp for generic ingestion.
- `cisco`: recognises ASA/IOS patterns for action/severity and network tuples.
- `linux`: highlights authentication, auditd, and sudo activity.
- `f5`: captures client/server addressing and virtual server names from BIG-IP style logs.
- `vmware`: surfaces hypervisor user and VM identifiers.

Extend the mapping layer with a JSON or YAML override:

```bash
syslogcef --mapping-file resources/custom-linux.yaml --source linux
```

Override files support Python format strings, so keys such as `name: "Auth event from {host}"`
render using event fields. When both JSON and YAML files are provided, YAML support requires
installing `PyYAML`.

## Error handling

- Non-strict mode converts malformed lines into CEF with `flexString1Label=error`, `flexString1`
  describing the failure, and includes the original payload in `rawEvent` for debugging.
- `--strict` stops on the first parse error and returns a non-zero exit code—ideal for CI pipelines.
- Processed and failed counts are available through `--stats` (stderr) and from the CLI return
  object when embedding the `main()` helper.

## Performance and benchmarking

Tips for squeezing out throughput:

- Use `--workers` when mappings are CPU-bound; performance scales with available cores.
- Pipe data directly to the CLI (`gzip -dc file.gz | syslogcef ...`) to avoid intermediate files.
- Prefer JSON input when possible—structured key/value extraction is cheaper than regex parsing.

Benchmark helper:

```bash
python scripts/bench.py tests/data/cisco-ios.log --lines 10000
```

On a sample dataset (`tests/data/cisco-ios.log`) processed with
`python scripts/bench.py --lines 50000` on an Apple M2 (Python 3.11) the converter sustains roughly
220k lines/sec in single-threaded mode.

## Sample data & rsyslog templates

Fixtures used by the test suite are available under `tests/data`, sourced from the original
`json-logs/` and `syslog-logs/` directories. For rsyslog configuration snippets compatible with the
tooling see [RSYSLOG_TEMPLATES.md](RSYSLOG_TEMPLATES.md).

## Development workflow

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

ruff check src tests
black src tests
mypy src
pytest
```

Pre-commit hooks (`pre-commit install`) run the same checks locally as the CI workflow defined in
`.github/workflows/ci.yml`.

## Contributing

Issues and pull requests are welcome. Please include tests for bug fixes and new features and update
the [CHANGELOG](CHANGELOG.md) in reverse chronological order. For significant mapping changes, attach
sample log lines to help reviewers validate the behaviour.

## License

Apache License 2.0. See [LICENSE](LICENSE).
