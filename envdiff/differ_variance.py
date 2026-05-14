"""Compute value variance across multiple env files for shared keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class VarianceEntry:
    key: str
    values: Dict[str, Optional[str]]  # filename -> value
    unique_values: List[Optional[str]] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"VarianceEntry(key={self.key!r}, unique={len(self.unique_values)})"

    @property
    def is_uniform(self) -> bool:
        """True when all envs agree on the same value."""
        return len(self.unique_values) <= 1

    @property
    def variance_count(self) -> int:
        """Number of distinct values seen across envs."""
        return len(self.unique_values)


@dataclass
class VarianceResult:
    filenames: List[str]
    entries: List[VarianceEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def uniform_count(self) -> int:
        return sum(1 for e in self.entries if e.is_uniform)

    @property
    def variant_count(self) -> int:
        return sum(1 for e in self.entries if not e.is_uniform)

    @property
    def is_uniform(self) -> bool:
        return self.variant_count == 0

    def get(self, key: str) -> Optional[VarianceEntry]:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def build_variance(envs: List[Dict[str, Optional[str]]], filenames: List[str]) -> VarianceResult:
    """Build a VarianceResult from a list of env dicts and their labels."""
    if len(envs) != len(filenames):
        raise ValueError("envs and filenames must have the same length")

    all_keys: List[str] = sorted({k for env in envs for k in env})
    entries: List[VarianceEntry] = []

    for key in all_keys:
        values: Dict[str, Optional[str]] = {
            fname: env.get(key) for fname, env in zip(filenames, envs)
        }
        unique = list(dict.fromkeys(values.values()))  # ordered dedup
        entries.append(VarianceEntry(key=key, values=values, unique_values=unique))

    return VarianceResult(filenames=filenames, entries=entries)
