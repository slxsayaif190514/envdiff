"""Symmetry analysis: checks how symmetric two env files are in terms of shared keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class SymmetryEntry:
    key: str
    in_a: bool
    in_b: bool
    value_a: str | None
    value_b: str | None

    def __repr__(self) -> str:
        return f"SymmetryEntry(key={self.key!r}, in_a={self.in_a}, in_b={self.in_b})"

    @property
    def is_shared(self) -> bool:
        return self.in_a and self.in_b

    @property
    def is_exclusive_a(self) -> bool:
        return self.in_a and not self.in_b

    @property
    def is_exclusive_b(self) -> bool:
        return self.in_b and not self.in_a

    @property
    def values_match(self) -> bool:
        return self.is_shared and self.value_a == self.value_b


@dataclass
class SymmetryResult:
    file_a: str
    file_b: str
    entries: list[SymmetryEntry] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    @property
    def shared_keys(self) -> list[SymmetryEntry]:
        return [e for e in self.entries if e.is_shared]

    @property
    def exclusive_a(self) -> list[SymmetryEntry]:
        return [e for e in self.entries if e.is_exclusive_a]

    @property
    def exclusive_b(self) -> list[SymmetryEntry]:
        return [e for e in self.entries if e.is_exclusive_b]

    @property
    def symmetry_ratio(self) -> float:
        if self.total_keys == 0:
            return 1.0
        return len(self.shared_keys) / self.total_keys

    @property
    def is_symmetric(self) -> bool:
        return self.symmetry_ratio == 1.0


def compute_symmetry(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    file_a: str = "a",
    file_b: str = "b",
) -> SymmetryResult:
    all_keys: Set[str] = set(env_a) | set(env_b)
    entries = [
        SymmetryEntry(
            key=k,
            in_a=k in env_a,
            in_b=k in env_b,
            value_a=env_a.get(k),
            value_b=env_b.get(k),
        )
        for k in sorted(all_keys)
    ]
    return SymmetryResult(file_a=file_a, file_b=file_b, entries=entries)
