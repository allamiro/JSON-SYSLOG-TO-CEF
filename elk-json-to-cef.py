#!/usr/bin/env python3
"""Compatibility wrapper pointing to the new syslogcef CLI."""

from syslogcef.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
