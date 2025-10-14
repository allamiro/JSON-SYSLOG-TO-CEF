from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from collections.abc import Iterable, Iterator
from collections.abc import Mapping as MappingABC
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import tzinfo
from pathlib import Path

try:  # pragma: no cover - optional dependency
    from dateutil import tz
except ImportError:  # pragma: no cover
    from zoneinfo import ZoneInfo

    class _TZModule:
        @staticmethod
        def gettz(name: str | None):
            if not name:
                return None
            try:
                return ZoneInfo(name)
            except Exception:
                return None

    tz = _TZModule()  # type: ignore[assignment]

from .converters import (
    DEFAULT_PRODUCT,
    DEFAULT_VENDOR,
    DEFAULT_VERSION,
    convert_line,
    from_json,
    parse_syslog,
    to_cef,
)
from .mappings import get_mapping
from .mappings.base import Mapping, MappingResult, load_mapping_file
from .utils import ParsedEvent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert syslog or JSON events to CEF")
    parser.add_argument("--input", "-i", default="-", help="Input file or - for stdin")
    parser.add_argument("--output", "-o", default="-", help="Output file or - for stdout")
    parser.add_argument(
        "--format", choices=["syslog", "json"], default=None, help="Force input format"
    )
    parser.add_argument("--vendor", default=DEFAULT_VENDOR)
    parser.add_argument("--product", default=DEFAULT_PRODUCT)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--source",
        default="default",
        help="Source mapping to use (cisco, linux, f5, vmware, default)",
    )
    parser.add_argument("--watch", action="store_true", help="Tail the input file for new lines")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker threads")
    parser.add_argument("--tz", dest="timezone", help="Default timezone for naive timestamps")
    parser.add_argument("--strict", action="store_true", help="Fail on parse errors")
    parser.add_argument("--stats", action="store_true", help="Print statistics to stderr")
    parser.add_argument("--mapping-file", help="Additional mapping overrides (JSON or YAML)")
    return parser


class OverrideMapping:
    def __init__(self, base: Mapping, overrides: dict[str, str]):
        self.base = base
        self.overrides = overrides
        self.name = base.name

    def map(self, event: ParsedEvent) -> MappingResult:
        base_result: MappingResult = self.base.map(event)
        extensions = dict(base_result.extensions)
        if self.overrides:
            safe_map = defaultdict(str, event.fields)
            for key, value in self.overrides.items():
                try:
                    extensions[key] = str(value).format_map(safe_map)
                except KeyError:
                    extensions[key] = value
        return MappingResult(
            signature_id=base_result.signature_id,
            name=base_result.name,
            severity=base_result.severity,
            extensions=extensions,
        )


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    default_tz = tz.gettz(args.timezone) if args.timezone else None

    base_mapping = get_mapping(args.source)
    mapping: Mapping = base_mapping
    if args.mapping_file:
        overrides = load_mapping_file(args.mapping_file)
        mapping = OverrideMapping(base_mapping, overrides)

    input_iter = open_input(args.input, watch=args.watch)
    output_stream = (
        sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8")
    )

    executor: Executor | None = None
    if args.workers and args.workers > 1:
        executor = ThreadPoolExecutor(max_workers=args.workers)

    processed = 0
    failed = 0

    try:
        if executor:
            futures = []
            for line in input_iter:
                futures.append(
                    executor.submit(
                        convert_single,
                        line,
                        mapping,
                        args,
                        default_tz,
                    )
                )
            for future in futures:
                try:
                    cef_line = future.result()
                    processed += 1
                    failed += int("flexString1=parse_error" in cef_line)
                    output_stream.write(cef_line + "\n")
                except Exception:
                    if args.strict:
                        raise
                    failed += 1
        else:
            for line in input_iter:
                cef_line = convert_single(line, mapping, args, default_tz)
                processed += 1
                failed += int("flexString1=parse_error" in cef_line)
                output_stream.write(cef_line + "\n")
    finally:
        if output_stream is not sys.stdout:
            output_stream.close()
        if executor:
            executor.shutdown()

    if args.stats:
        sys.stderr.write(f"processed={processed} failed={failed}\n")
    return 0


def open_input(path: str, *, watch: bool) -> Iterator[str]:
    if path == "-":
        return iter(sys.stdin.readline, "")
    file_path = Path(path)
    file = file_path.open("r", encoding="utf-8", errors="replace")
    if not watch:
        return iter(file.readline, "")

    def watcher() -> Iterator[str]:
        while True:
            line = file.readline()
            if line:
                yield line
            else:
                time.sleep(0.5)

    return watcher()


def convert_single(
    line: str,
    mapping: Mapping,
    args: argparse.Namespace,
    default_tz: tzinfo | None,
) -> str:
    if args.format:
        try:
            if args.format == "json":
                data = json.loads(line)
                if not isinstance(data, MappingABC):
                    raise ValueError("JSON log line must be an object")
                event = from_json(data, default_tz=default_tz)
            else:
                event = parse_syslog(line, default_tz=default_tz).as_event(default_tz)
            return to_cef(
                event,
                vendor=args.vendor,
                product=args.product,
                version=args.version,
                mapping=mapping,
            )
        except Exception:
            if args.strict:
                raise
            # fall back to automatic conversion
    return convert_line(
        line,
        args.source,
        mapping,
        vendor=args.vendor,
        product=args.product,
        version=args.version,
        default_tz=default_tz,
        strict=args.strict,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
