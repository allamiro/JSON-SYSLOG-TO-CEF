from __future__ import annotations

from typing import Dict

from .base import BaseMapping, Mapping, MappingResult
from .cisco import CiscoMapping, mapping as cisco
from .default import DefaultMapping, mapping as default
from .f5 import F5Mapping, mapping as f5
from .linux import LinuxMapping, mapping as linux
from .vmware import VMwareMapping, mapping as vmware

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

_REGISTRY: Dict[str, BaseMapping] = {
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
        raise KeyError(f"Unknown mapping '{name}'")
