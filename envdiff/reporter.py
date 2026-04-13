"""Generate summary reports from comparison results."""

from dataclasses import dataclass, field
from typing import List
from envdiff.comparator import CompareResult


@dataclass
class ReportSummary:
    total_keys: int
    missing_in_b: int
    missing_in_a: int
    mismatches: int
    files: List[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return self.missing_in_b > 0 or self.missing_in_a > 0 or self.mismatches > 0

    @property
    def issue_count(self) -> int:
        return self.missing_in_b + self.missing_in_a + self.mismatches


def build_summary(result: CompareResult, file_a: str, file_b: str) -> ReportSummary:
    """Build a ReportSummary from a CompareResult and file paths."""
    all_keys = set()
    for diff in result.diffs:
        all_keys.add(diff.key)

    # total unique keys seen across both files is approximated via diffs
    # plus matched keys (no diff recorded for matching keys)
    total = len(all_keys) + result.matched_count

    return ReportSummary(
        total_keys=total,
        missing_in_b=len(result.missing_in_b),
        missing_in_a=len(result.missing_in_a),
        mismatches=len(result.mismatches),
        files=[file_a, file_b],
    )


def format_summary(summary: ReportSummary) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Comparing: {summary.files[0]}  vs  {summary.files[1]}",
        f"Total keys checked : {summary.total_keys}",
        f"Missing in B       : {summary.missing_in_b}",
        f"Missing in A       : {summary.missing_in_a}",
        f"Mismatched values  : {summary.mismatches}",
    ]
    if summary.has_issues:
        lines.append(f"\n{summary.issue_count} issue(s) found.")
    else:
        lines.append("\nAll keys match — no issues found.")
    return "\n".join(lines)
