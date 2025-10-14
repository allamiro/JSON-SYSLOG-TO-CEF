#!/usr/bin/env python3
"""Compatibility wrapper for the legacy syslog-to-cef script."""

from syslogcef.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
