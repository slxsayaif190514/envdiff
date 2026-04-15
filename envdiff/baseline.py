"""Baseline comparison: compare current env against a saved snapshot baseline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.snapshotter import Snapshot


@dataclass
class BaselineDiff:
    key: str
    baseline_value: Optional[str]
    current_value: Optional[str]
    kind: str  # "added", "removed", "changed"

    def __repr__(self) -> str:  # pragma: no cover
        return f"BaselineDiff(key={self.key!r}, kind={self.kind!r})"


@dataclass
class BaselineResult:
    snapshot_label: str
    env_file: str
    added: List[BaselineDiff] = field(default_factory=list)
    removed: List[BaselineDiff] = field(default_factory=list)
    changed: List[BaselineDiff] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not (self.added or self.removed or self.changed)

    @property
    def issue_count(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


def compare_against_baseline(
    snapshot: Snapshot,
    current_env: Dict[str, str],
    env_file: str = "",
) -> BaselineResult:
    """Compare *current_env* dict against the env stored in *snapshot*."""
    baseline_env: Dict[str, str] = {}
    for entry in snapshot.diffs:
        # Snapshots store CompareResult diffs; reconstruct a flat env from
        # the file_a perspective (keys present in the baseline).
        if entry.get("type") in ("match", "mismatch", "missing_in_b"):
            key = entry["key"]
            baseline_env[key] = entry.get("value_a") or ""

    result = BaselineResult(
        snapshot_label=snapshot.label,
        env_file=env_file,
    )

    all_keys = set(baseline_env) | set(current_env)
    for key in sorted(all_keys):
        in_baseline = key in baseline_env
        in_current = key in current_env

        if in_baseline and not in_current:
            result.removed.append(
                BaselineDiff(key=key, baseline_value=baseline_env[key], current_value=None, kind="removed")
            )
        elif in_current and not in_baseline:
            result.added.append(
                BaselineDiff(key=key, baseline_value=None, current_value=current_env[key], kind="added")
            )
        elif baseline_env[key] != current_env[key]:
            result.changed.append(
                BaselineDiff(key=key, baseline_value=baseline_env[key], current_value=current_env[key], kind="changed")
            )

    return result
