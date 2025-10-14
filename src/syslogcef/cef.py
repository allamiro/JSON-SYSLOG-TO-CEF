from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Tuple

from .utils import sanitize_text

__all__ = [
    "CEFHeader",
    "escape_cef_header",
    "escape_cef_extension",
    "format_extensions",
    "priority_to_severity",
    "build_cef",
]


@dataclass(slots=True)
class CEFHeader:
    device_vendor: str
    device_product: str
    device_version: str
    signature_id: str
    name: str
    severity: int
    version: int = 0

    def as_str(self) -> str:
        severity = max(0, min(self.severity, 10))
        parts = [
            f"CEF:{self.version}",
            escape_cef_header(self.device_vendor),
            escape_cef_header(self.device_product),
            escape_cef_header(self.device_version),
            escape_cef_header(self.signature_id),
            escape_cef_header(self.name),
            str(severity),
        ]
        return "|".join(parts)


_HEADER_ESCAPE = str.maketrans({"\\": r"\\\\", "|": r"\|", "=": r"\="})
_EXTENSION_ESCAPE = str.maketrans({"\\": r"\\\\", "=": r"\="})


def escape_cef_header(value: str) -> str:
    return sanitize_text(value).translate(_HEADER_ESCAPE)


def escape_cef_extension(value: str) -> str:
    return sanitize_text(value).translate(_EXTENSION_ESCAPE)


def normalize_extension_key(key: str) -> str:
    normalized = [ch for ch in key if ch.isalnum() or ch in {"_", "-"}]
    if not normalized:
        return "cs1"
    if normalized[0].isdigit():
        normalized.insert(0, "f")
    return "".join(normalized)[:1023]


def format_extensions(pairs: Mapping[str, str] | Iterable[Tuple[str, str]]) -> str:
    if isinstance(pairs, Mapping):
        items = pairs.items()
    else:
        items = list(pairs)
    return " ".join(
        f"{normalize_extension_key(key)}={escape_cef_extension(str(value))}"
        for key, value in items
        if value is not None and value != ""
    )


def priority_to_severity(priority: int | None) -> int:
    if priority is None:
        return 3
    # RFC5424: priority = facility * 8 + severity (0 emerg - 7 debug)
    syslog_severity = priority % 8
    mapping = {
        0: 10,
        1: 9,
        2: 8,
        3: 7,
        4: 5,
        5: 3,
        6: 2,
        7: 1,
    }
    return mapping.get(syslog_severity, 3)


def build_cef(
    header: CEFHeader,
    extensions: Mapping[str, str] | Iterable[Tuple[str, str]] | None = None,
) -> str:
    payload = header.as_str()
    if extensions:
        payload += " " + format_extensions(extensions)
    return payload
