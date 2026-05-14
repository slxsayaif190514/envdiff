"""Compute value-density metrics for .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DensityEntry:
    key: str
    value: str
    length: int
    is_empty: bool
    is_short: bool   # length < 8
    is_long: bool    # length >= 64

    def __repr__(self) -> str:  # pragma: no cover
        return f"DensityEntry({self.key!r}, len={self.length})"


@dataclass
class DensityResult:
    filename: str
    entries: List[DensityEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def empty_count(self) -> int:
        return sum(1 for e in self.entries if e.is_empty)

    @property
    def short_count(self) -> int:
        return sum(1 for e in self.entries if e.is_short and not e.is_empty)

    @property
    def long_count(self) -> int:
        return sum(1 for e in self.entries if e.is_long)

    @property
    def average_length(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.length for e in self.entries) / len(self.entries)

    def get(self, key: str) -> DensityEntry | None:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def _make_entry(key: str, value: str) -> DensityEntry:
    length = len(value)
    return DensityEntry(
        key=key,
        value=value,
        length=length,
        is_empty=length == 0,
        is_short=0 < length < 8,
        is_long=length >= 64,
    )


def build_density(env: Dict[str, str], filename: str = "") -> DensityResult:
    entries = [_make_entry(k, v) for k, v in sorted(env.items())]
    return DensityResult(filename=filename, entries=entries)
