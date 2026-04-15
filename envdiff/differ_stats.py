"""Statistics aggregator for diff results."""
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.comparator import CompareResult, KeyDiff


@dataclass
class DiffStats:
    total_keys: int = 0
    matched: int = 0
    missing_in_a: int = 0
    missing_in_b: int = 0
    mismatched: int = 0
    files: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return (self.missing_in_a + self.missing_in_b + self.mismatched) > 0

    @property
    def issue_count(self) -> int:
        return self.missing_in_a + self.missing_in_b + self.mismatched

    @property
    def match_rate(self) -> float:
        if self.total_keys == 0:
            return 100.0
        return round(self.matched / self.total_keys * 100, 1)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DiffStats(total={self.total_keys}, matched={self.matched}, "
            f"missing_a={self.missing_in_a}, missing_b={self.missing_in_b}, "
            f"mismatched={self.mismatched})"
        )


def compute_stats(result: CompareResult, file_a: str = "", file_b: str = "") -> DiffStats:
    """Compute statistics from a CompareResult."""
    all_keys: Dict[str, KeyDiff] = {}

    for d in result.missing_in_b:
        all_keys[d.key] = d
    for d in result.missing_in_a:
        all_keys[d.key] = d
    for d in result.mismatches:
        all_keys[d.key] = d
    for d in result.matching:
        all_keys[d.key] = d

    stats = DiffStats(
        total_keys=len(all_keys),
        matched=len(result.matching),
        missing_in_a=len(result.missing_in_a),
        missing_in_b=len(result.missing_in_b),
        mismatched=len(result.mismatches),
        files=[f for f in [file_a, file_b] if f],
    )
    return stats
