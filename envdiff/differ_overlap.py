"""Computes key overlap statistics between two env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set

from envdiff.comparator import CompareResult


@dataclass
class OverlapResult:
    file_a: str
    file_b: str
    shared_keys: Set[str] = field(default_factory=set)
    only_in_a: Set[str] = field(default_factory=set)
    only_in_b: Set[str] = field(default_factory=set)
    value_matches: Set[str] = field(default_factory=set)
    value_mismatches: Set[str] = field(default_factory=set)

    @property
    def total_unique_keys(self) -> int:
        return len(self.shared_keys | self.only_in_a | self.only_in_b)

    @property
    def overlap_ratio(self) -> float:
        """Fraction of total unique keys that appear in both files."""
        total = self.total_unique_keys
        if total == 0:
            return 1.0
        return len(self.shared_keys) / total

    @property
    def value_match_ratio(self) -> float:
        """Among shared keys, fraction whose values are identical."""
        if not self.shared_keys:
            return 1.0
        return len(self.value_matches) / len(self.shared_keys)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"OverlapResult(shared={len(self.shared_keys)}, "
            f"only_a={len(self.only_in_a)}, only_b={len(self.only_in_b)}, "
            f"overlap={self.overlap_ratio:.0%})"
        )


def compute_overlap(
    result: CompareResult,
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    file_a: str = "a",
    file_b: str = "b",
) -> OverlapResult:
    """Build an OverlapResult from a CompareResult and the two raw env dicts."""
    only_in_a: Set[str] = {d.key for d in result.missing_in_b}
    only_in_b: Set[str] = {d.key for d in result.missing_in_a}
    mismatch_keys: Set[str] = {d.key for d in result.mismatches}

    all_a = set(env_a)
    all_b = set(env_b)
    shared = all_a & all_b

    value_matches: Set[str] = shared - mismatch_keys
    value_mismatches: Set[str] = shared & mismatch_keys

    return OverlapResult(
        file_a=file_a,
        file_b=file_b,
        shared_keys=shared,
        only_in_a=only_in_a,
        only_in_b=only_in_b,
        value_matches=value_matches,
        value_mismatches=value_mismatches,
    )
