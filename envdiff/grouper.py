"""Group env keys by prefix or namespace for structured comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import CompareResult, KeyDiff


@dataclass
class KeyGroup:
    prefix: str
    diffs: List[KeyDiff] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.diffs)

    @property
    def has_issues(self) -> bool:
        return any(d.diff_type != "match" for d in self.diffs)

    def __repr__(self) -> str:  # pragma: no cover
        return f"KeyGroup(prefix={self.prefix!r}, keys={self.key_count})"


@dataclass
class GroupResult:
    groups: Dict[str, KeyGroup] = field(default_factory=dict)
    ungrouped: List[KeyDiff] = field(default_factory=list)

    @property
    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    @property
    def total_keys(self) -> int:
        return sum(g.key_count for g in self.groups.values()) + len(self.ungrouped)


def _extract_prefix(key: str, separator: str = "_") -> str | None:
    """Return the first segment before separator, or None if no separator."""
    if separator in key:
        return key.split(separator, 1)[0]
    return None


def group_result(
    result: CompareResult,
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupResult:
    """Group all diffs from a CompareResult by key prefix."""
    all_diffs: List[KeyDiff] = (
        result.missing_in_b + result.missing_in_a + result.mismatches + result.matches
    )

    raw: Dict[str, List[KeyDiff]] = {}
    ungrouped: List[KeyDiff] = []

    for diff in all_diffs:
        prefix = _extract_prefix(diff.key, separator)
        if prefix is None:
            ungrouped.append(diff)
        else:
            raw.setdefault(prefix, []).append(diff)

    groups: Dict[str, KeyGroup] = {}
    for prefix, diffs in raw.items():
        if len(diffs) >= min_group_size:
            groups[prefix] = KeyGroup(prefix=prefix, diffs=diffs)
        else:
            ungrouped.extend(diffs)

    return GroupResult(groups=groups, ungrouped=ungrouped)
