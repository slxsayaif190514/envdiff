"""Compares .env files by the 'age' (staleness) of their keys based on snapshot metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class AgeEntry:
    key: str
    last_seen: Optional[datetime]
    first_seen: Optional[datetime]
    snapshot_count: int

    def __repr__(self) -> str:
        return (
            f"AgeEntry(key={self.key!r}, last_seen={self.last_seen}, "
            f"first_seen={self.first_seen}, snapshots={self.snapshot_count})"
        )

    @property
    def age_days(self) -> Optional[float]:
        if self.first_seen is None or self.last_seen is None:
            return None
        delta = self.last_seen - self.first_seen
        return delta.total_seconds() / 86400

    @property
    def is_stale(self) -> bool:
        """Considered stale if seen only once or age exceeds 90 days."""
        if self.snapshot_count <= 1:
            return False
        days = self.age_days
        return days is not None and days > 90


@dataclass
class AgeResult:
    filename: str
    entries: List[AgeEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def stale_keys(self) -> List[AgeEntry]:
        return [e for e in self.entries if e.is_stale]

    @property
    def stale_count(self) -> int:
        return len(self.stale_keys)

    @property
    def is_clean(self) -> bool:
        return self.stale_count == 0


def build_age_result(
    filename: str,
    snapshots: List[Dict[str, str]],
    timestamps: List[datetime],
) -> AgeResult:
    """Build an AgeResult from a list of env snapshots and their timestamps."""
    if len(snapshots) != len(timestamps):
        raise ValueError("snapshots and timestamps must have the same length")

    key_first: Dict[str, datetime] = {}
    key_last: Dict[str, datetime] = {}
    key_count: Dict[str, int] = {}

    for snap, ts in zip(snapshots, timestamps):
        for key in snap:
            if key not in key_first:
                key_first[key] = ts
            key_last[key] = ts
            key_count[key] = key_count.get(key, 0) + 1

    all_keys = sorted(key_first.keys())
    entries = [
        AgeEntry(
            key=k,
            first_seen=key_first[k],
            last_seen=key_last[k],
            snapshot_count=key_count[k],
        )
        for k in all_keys
    ]
    return AgeResult(filename=filename, entries=entries)
