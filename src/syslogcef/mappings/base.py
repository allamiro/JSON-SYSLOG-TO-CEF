from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..cef import priority_to_severity
from ..utils import ParsedEvent, sanitize_text

__all__ = ["Mapping", "MappingResult", "BaseMapping", "load_mapping_file"]


@dataclass(slots=True)
class MappingResult:
    signature_id: str
    name: str
    severity: int
    extensions: dict[str, str]


class Mapping(Protocol):
    name: str

    def map(self, event: ParsedEvent) -> MappingResult: ...


class BaseMapping:
    name = "base"

    def map(self, event: ParsedEvent) -> MappingResult:  # pragma: no cover - to override
        severity = priority_to_severity(event.priority)
        return MappingResult(
            signature_id="generic",
            name=sanitize_text(event.message)[:1024] or "Generic Event",
            severity=severity,
            extensions={"msg": sanitize_text(event.message)},
        )


def load_mapping_file(path: str | Path) -> dict[str, str]:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if file_path.suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("PyYAML required for YAML mapping files") from exc
        data = yaml.safe_load(text)
    else:
        import json

        data = json.loads(text)
    if not isinstance(data, MappingABC):
        raise ValueError("Mapping file must contain a dictionary")
    return {str(k): sanitize_text(v) for k, v in data.items()}
