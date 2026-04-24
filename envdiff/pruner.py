"""Pruner: remove keys from an env dict that match a set of patterns or exact names."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PruneEntry:
    key: str
    value: str
    reason: str  # 'exact' | 'pattern'

    def __repr__(self) -> str:  # pragma: no cover
        return f"PruneEntry(key={self.key!r}, reason={self.reason!r})"


@dataclass
class PruneResult:
    filename: str
    kept: Dict[str, str] = field(default_factory=dict)
    removed: List[PruneEntry] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.removed) == 0

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def removed_keys(self) -> List[str]:
        return sorted(e.key for e in self.removed)


def prune_env(
    env: Dict[str, str],
    filename: str,
    exact: List[str] | None = None,
    patterns: List[str] | None = None,
) -> PruneResult:
    """Remove keys from *env* that appear in *exact* or match any glob in *patterns*."""
    exact_set = set(exact or [])
    glob_list = list(patterns or [])

    result = PruneResult(filename=filename)

    for key, value in env.items():
        if key in exact_set:
            result.removed.append(PruneEntry(key=key, value=value, reason="exact"))
            continue

        matched_pattern = next(
            (p for p in glob_list if fnmatch.fnmatch(key, p)), None
        )
        if matched_pattern is not None:
            result.removed.append(PruneEntry(key=key, value=value, reason="pattern"))
            continue

        result.kept[key] = value

    return result
