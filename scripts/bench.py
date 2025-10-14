from __future__ import annotations

import argparse
import time
from pathlib import Path

from syslogcef.converters import convert_line


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark syslogcef conversion speed")
    parser.add_argument("path", help="Path to log file")
    parser.add_argument("--lines", type=int, default=10000, help="Number of lines to read")
    parser.add_argument("--source", default="default", help="Mapping source to use")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.path)
    count = 0
    start = time.perf_counter()
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            convert_line(line, source=args.source)
            count += 1
            if count >= args.lines:
                break
    elapsed = time.perf_counter() - start
    rate = count / elapsed if elapsed else 0
    print(f"processed={count} lines elapsed={elapsed:.3f}s rate={rate:.0f} lines/s")


if __name__ == "__main__":
    main()
