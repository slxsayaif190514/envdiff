"""Timeline: track how a key's value has changed across multiple snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.snapshotter import Snapshot


@dataclass
class TimelineEntry:
    snapshot_label: str
    value: Optional[str]  # None means key was absent

    def __repr__(self) -> str:  # pragma: no cover
        val = repr(self.value) if self.value is not None else "<absent>"
        return f"TimelineEntry({self.snapshot_label!r}, {val})"


@dataclass
class KeyTimeline:
    key: str
    entries: List[TimelineEntry] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        """Number of times the value changed between consecutive snapshots."""
        changes = 0
        for i in range(1, len(self.entries)):
            if self.entries[i].value != self.entries[i - 1].value:
                changes += 1
        return changes

    @property
    def is_stable(self) -> bool:
        return self.change_count == 0

    @property
    def latest_value(self) -> Optional[str]:
        if not self.entries:
            return None
        return self.entries[-1].value


@dataclass
class TimelineResult:
    timelines: List[KeyTimeline] = field(default_factory=list)

    @property
    def unstable_keys(self) -> List[KeyTimeline]:
        return [t for t in self.timelines if not t.is_stable]

    @property
    def stable_keys(self) -> List[KeyTimeline]:
        return [t for t in self.timelines if t.is_stable]


def build_timeline(snapshots: List[Snapshot]) -> TimelineResult:
    """Build a per-key timeline across an ordered list of snapshots."""
    all_keys: set = set()
    for snap in snapshots:
        all_keys.update(snap.env_a.keys())
        all_keys.update(snap.env_b.keys())

    timelines: List[KeyTimeline] = []
    for key in sorted(all_keys):
        entries: List[TimelineEntry] = []
        for snap in snapshots:
            combined = {**snap.env_a, **snap.env_b}
            value = combined.get(key, None)
            entries.append(TimelineEntry(snapshot_label=snap.label, value=value))
        timelines.append(KeyTimeline(key=key, entries=entries))

    return TimelineResult(timelines=timelines)
