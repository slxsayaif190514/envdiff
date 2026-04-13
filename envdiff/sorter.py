"""Sorting utilities for CompareResult diffs."""

from enum import Enum
from typing import List

from envdiff.comparator import CompareResult, KeyDiff


class SortKey(str, Enum):
    KEY = "key"
    TYPE = "type"
    STATUS = "status"


_TYPE_ORDER = {"missing_in_b": 0, "missing_in_a": 1, "mismatch": 2}


def _diff_sort_key(diff: KeyDiff, by: SortKey):
    if by == SortKey.KEY:
        return diff.key.lower()
    if by == SortKey.TYPE:
        return (_TYPE_ORDER.get(diff.diff_type, 99), diff.key.lower())
    if by == SortKey.STATUS:
        # group by whether values are present in both sides
        has_both = diff.value_a is not None and diff.value_b is not None
        return (0 if has_both else 1, diff.key.lower())
    return diff.key.lower()


def sort_result(
    result: CompareResult,
    by: SortKey = SortKey.KEY,
    reverse: bool = False,
) -> CompareResult:
    """Return a new CompareResult with diffs sorted by the given key."""
    all_diffs: List[KeyDiff] = (
        result.missing_in_b + result.missing_in_a + result.mismatches
    )
    sorted_diffs = sorted(all_diffs, key=lambda d: _diff_sort_key(d, by), reverse=reverse)

    new_missing_b = [d for d in sorted_diffs if d.diff_type == "missing_in_b"]
    new_missing_a = [d for d in sorted_diffs if d.diff_type == "missing_in_a"]
    new_mismatches = [d for d in sorted_diffs if d.diff_type == "mismatch"]

    return CompareResult(
        missing_in_b=new_missing_b,
        missing_in_a=new_missing_a,
        mismatches=new_mismatches,
    )
