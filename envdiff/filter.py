"""Filter utilities for envdiff comparisons.

Allows users to narrow down diff results by key prefix, pattern, or
diff type (missing/mismatch), making it easier to focus on what matters.
"""

from __future__ import annotations

import fnmatch
from typing import List, Optional

from envdiff.comparator import CompareResult, KeyDiff


def filter_by_prefix(result: CompareResult, prefix: str) -> CompareResult:
    """Return a new CompareResult keeping only keys that start with *prefix*."""
    prefix_upper = prefix.upper()

    def _keep(key: str) -> bool:
        return key.upper().startswith(prefix_upper)

    return CompareResult(
        missing_in_b=[d for d in result.missing_in_b if _keep(d.key)],
        missing_in_a=[d for d in result.missing_in_a if _keep(d.key)],
        mismatches=[d for d in result.mismatches if _keep(d.key)],
    )


def filter_by_pattern(result: CompareResult, pattern: str) -> CompareResult:
    """Return a new CompareResult keeping only keys matching a glob *pattern*."""
    pattern_upper = pattern.upper()

    def _keep(key: str) -> bool:
        return fnmatch.fnmatch(key.upper(), pattern_upper)

    return CompareResult(
        missing_in_b=[d for d in result.missing_in_b if _keep(d.key)],
        missing_in_a=[d for d in result.missing_in_a if _keep(d.key)],
        mismatches=[d for d in result.mismatches if _keep(d.key)],
    )


def filter_by_type(
    result: CompareResult,
    *,
    include_missing_b: bool = True,
    include_missing_a: bool = True,
    include_mismatches: bool = True,
) -> CompareResult:
    """Return a new CompareResult keeping only the requested diff types."""
    return CompareResult(
        missing_in_b=result.missing_in_b if include_missing_b else [],
        missing_in_a=result.missing_in_a if include_missing_a else [],
        mismatches=result.mismatches if include_mismatches else [],
    )
