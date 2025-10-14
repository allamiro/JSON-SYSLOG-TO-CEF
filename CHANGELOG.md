# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-06-06
### Added
- Initial Python package layout with `syslogcef` module and CLI.
- RFC3164/RFC5424 parsers with key/value and structured data extraction.
- CEF encoder with deterministic severity mapping and escaping.
- Mapping framework plus default, Cisco, Linux, F5 and VMware implementations.
- Streaming CLI with watch mode, worker pool, stats and mapping overrides.
- Test suite covering parsing, encoding, converters and CLI.
- Pre-commit configuration, CI workflow, benchmark helper and updated documentation.
