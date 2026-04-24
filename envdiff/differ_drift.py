"""Detect value drift between two env snapshots over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DriftEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    drift_type: str  # 'changed', 'added', 'removed'

    def __repr__(self) -> str:
        return f"DriftEntry({self.key!r}, {self.drift_type})"


@dataclass
class DriftResult:
    source_label: str
    target_label: str
    entries: List[DriftEntry] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.entries) == 0

    @property
    def drift_count(self) -> int:
        return len(self.entries)

    def by_type(self, drift_type: str) -> List[DriftEntry]:
        return [e for e in self.entries if e.drift_type == drift_type]

    def __repr__(self) -> str:
        return (
            f"DriftResult({self.source_label!r} -> {self.target_label!r}, "
            f"{self.drift_count} drifted)"
        )


def detect_drift(
    source: Dict[str, str],
    target: Dict[str, str],
    source_label: str = "source",
    target_label: str = "target",
) -> DriftResult:
    """Compare two env dicts and return a DriftResult describing changes."""
    result = DriftResult(source_label=source_label, target_label=target_label)

    all_keys = set(source) | set(target)
    for key in sorted(all_keys):
        in_source = key in source
        in_target = key in target

        if in_source and in_target:
            if source[key] != target[key]:
                result.entries.append(
                    DriftEntry(
                        key=key,
                        old_value=source[key],
                        new_value=target[key],
                        drift_type="changed",
                    )
                )
        elif in_target and not in_source:
            result.entries.append(
                DriftEntry(key=key, old_value=None, new_value=target[key], drift_type="added")
            )
        else:
            result.entries.append(
                DriftEntry(key=key, old_value=source[key], new_value=None, drift_type="removed")
            )

    return result
