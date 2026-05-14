"""Track key lineage across multiple env snapshots over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LineageEvent:
    snapshot_label: str
    value: Optional[str]  # None means key was absent

    def __repr__(self) -> str:
        val = repr(self.value) if self.value is not None else "<absent>"
        return f"LineageEvent(label={self.snapshot_label!r}, value={val})"


@dataclass
class LineageEntry:
    key: str
    events: List[LineageEvent] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"LineageEntry(key={self.key!r}, events={len(self.events)})"

    @property
    def first_seen(self) -> Optional[str]:
        for e in self.events:
            if e.value is not None:
                return e.snapshot_label
        return None

    @property
    def last_seen(self) -> Optional[str]:
        for e in reversed(self.events):
            if e.value is not None:
                return e.snapshot_label
        return None

    @property
    def change_count(self) -> int:
        changes = 0
        prev = None
        for e in self.events:
            if e.value != prev:
                if prev is not None or e.value is not None:
                    changes += 1
            prev = e.value
        return changes

    @property
    def is_stable(self) -> bool:
        values = [e.value for e in self.events if e.value is not None]
        return len(set(values)) <= 1


@dataclass
class LineageResult:
    labels: List[str]
    entries: Dict[str, LineageEntry] = field(default_factory=dict)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def unstable_keys(self) -> List[str]:
        return sorted(k for k, e in self.entries.items() if not e.is_stable)

    def get(self, key: str) -> Optional[LineageEntry]:
        return self.entries.get(key)


def build_lineage(
    snapshots: List[Dict[str, str]],
    labels: Optional[List[str]] = None,
) -> LineageResult:
    if labels is None:
        labels = [f"snap{i}" for i in range(len(snapshots))]
    if len(labels) != len(snapshots):
        raise ValueError("labels length must match snapshots length")

    all_keys: set = set()
    for snap in snapshots:
        all_keys.update(snap.keys())

    result = LineageResult(labels=labels)
    for key in sorted(all_keys):
        entry = LineageEntry(key=key)
        for label, snap in zip(labels, snapshots):
            entry.events.append(LineageEvent(snapshot_label=label, value=snap.get(key)))
        result.entries[key] = entry
    return result
