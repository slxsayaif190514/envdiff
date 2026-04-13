"""Support for ignoring specific keys during comparison."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable

from envdiff.comparator import CompareResult, KeyDiff


@dataclass
class IgnoreRules:
    """Collection of keys and patterns to ignore."""

    exact: set[str] = field(default_factory=set)
    patterns: list[str] = field(default_factory=list)

    def matches(self, key: str) -> bool:
        """Return True if *key* should be ignored."""
        if key in self.exact:
            return True
        return any(fnmatch.fnmatchcase(key, p) for p in self.patterns)


def build_ignore_rules(
    keys: Iterable[str] | None = None,
    patterns: Iterable[str] | None = None,
) -> IgnoreRules:
    """Create an :class:`IgnoreRules` from explicit keys and glob patterns."""
    return IgnoreRules(
        exact=set(keys or []),
        patterns=list(patterns or []),
    )


def _keep_diff(diff: KeyDiff, rules: IgnoreRules) -> bool:
    return not rules.matches(diff.key)


def apply_ignore(result: CompareResult, rules: IgnoreRules) -> CompareResult:
    """Return a new :class:`CompareResult` with ignored keys removed."""
    return CompareResult(
        missing_in_b=[d for d in result.missing_in_b if _keep_diff(d, rules)],
        missing_in_a=[d for d in result.missing_in_a if _keep_diff(d, rules)],
        mismatches=[d for d in result.mismatches if _keep_diff(d, rules)],
        matches=[d for d in result.matches if _keep_diff(d, rules)],
    )
