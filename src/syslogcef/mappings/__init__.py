from __future__ import annotations

from .base import BaseMapping, Mapping, MappingResult
from .cisco import mapping as cisco
from .default import mapping as default
from .f5 import mapping as f5
from .linux import mapping as linux
from .vmware import mapping as vmware

__all__ = [
    "BaseMapping",
    "Mapping",
    "MappingResult",
    "get_mapping",
    "cisco",
    "default",
    "f5",
    "linux",
    "vmware",
]

_REGISTRY: dict[str, BaseMapping] = {
    "default": default,
    "cisco": cisco,
    "linux": linux,
    "f5": f5,
    "vmware": vmware,
}


def get_mapping(name: str | None) -> BaseMapping:
    if not name:
        return default
    key = name.lower()
    try:
        return _REGISTRY[key]
    except KeyError:
        raise KeyError(f"Unknown mapping '{name}'") from None
