"""Score how similar two env files are, returning a 0–100 compatibility score."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from envdiff.comparator import CompareResult


@dataclass
class CompatibilityScore:
    total_keys: int
    matching_keys: int
    missing_in_b: int
    missing_in_a: int
    mismatched: int
    score: float  # 0.0 – 100.0

    def grade(self) -> str:
        if self.score >= 95:
            return "A"
        if self.score >= 80:
            return "B"
        if self.score >= 60:
            return "C"
        if self.score >= 40:
            return "D"
        return "F"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CompatibilityScore(score={self.score:.1f}, grade={self.grade()}, "
            f"total={self.total_keys})"
        )


def score_result(result: CompareResult) -> CompatibilityScore:
    """Compute a compatibility score from a CompareResult.

    Weights:
      - missing key (either side): full penalty
      - mismatched value: half penalty
    """
    n_missing_b = len(result.missing_in_b)
    n_missing_a = len(result.missing_in_a)
    n_mismatch = len(result.mismatches)

    all_keys: set = set()
    for d in result.missing_in_b:
        all_keys.add(d.key)
    for d in result.missing_in_a:
        all_keys.add(d.key)
    for d in result.mismatches:
        all_keys.add(d.key)
    for d in result.matches:
        all_keys.add(d.key)

    total = len(all_keys)
    if total == 0:
        return CompatibilityScore(
            total_keys=0,
            matching_keys=0,
            missing_in_b=0,
            missing_in_a=0,
            mismatched=0,
            score=100.0,
        )

    penalty = n_missing_b + n_missing_a + n_mismatch * 0.5
    raw_score = max(0.0, (total - penalty) / total * 100)

    return CompatibilityScore(
        total_keys=total,
        matching_keys=len(result.matches),
        missing_in_b=n_missing_b,
        missing_in_a=n_missing_a,
        mismatched=n_mismatch,
        score=round(raw_score, 2),
    )
