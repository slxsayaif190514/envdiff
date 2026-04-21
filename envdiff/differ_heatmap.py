"""Heatmap builder for env diff activity across multiple snapshots.

Builds a frequency map showing which keys change most often over time,
useful for identifying unstable or frequently-rotated config values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.snapshotter import Snapshot


@dataclass
class HeatmapEntry:
    """Tracks change frequency for a single key across snapshots."""

    key: str
    change_count: int
    total_snapshots: int
    last_value: Optional[str]

    @property
    def change_rate(self) -> float:
        """Fraction of snapshot transitions where this key changed."""
        if self.total_snapshots <= 1:
            return 0.0
        # transitions = total_snapshots - 1
        return self.change_count / (self.total_snapshots - 1)

    @property
    def heat_level(self) -> str:
        """Qualitative heat level: cold / warm / hot."""
        r = self.change_rate
        if r == 0.0:
            return "cold"
        if r < 0.5:
            return "warm"
        return "hot"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"HeatmapEntry(key={self.key!r}, changes={self.change_count}, "
            f"rate={self.change_rate:.2f}, level={self.heat_level!r})"
        )


@dataclass
class HeatmapResult:
    """Aggregated heatmap across a series of snapshots."""

    entries: List[HeatmapEntry] = field(default_factory=list)
    snapshot_count: int = 0

    @property
    def hot_keys(self) -> List[str]:
        """Keys with heat_level == 'hot', sorted alphabetically."""
        return sorted(e.key for e in self.entries if e.heat_level == "hot")

    @property
    def cold_keys(self) -> List[str]:
        """Keys that never changed across snapshots."""
        return sorted(e.key for e in self.entries if e.heat_level == "cold")

    @property
    def total_keys(self) -> int:
        return len(self.entries)

    def by_key(self, key: str) -> Optional[HeatmapEntry]:
        """Look up a single entry by key name."""
        for e in self.entries:
            if e.key == key:
                return e
        return None


def build_heatmap(snapshots: List[Snapshot]) -> HeatmapResult:
    """Build a HeatmapResult from an ordered list of Snapshot objects.

    Args:
        snapshots: Snapshots in chronological order (oldest first).

    Returns:
        HeatmapResult with per-key change frequencies.
    """
    if not snapshots:
        return HeatmapResult(entries=[], snapshot_count=0)

    # Collect all keys seen across every snapshot
    all_keys: set[str] = set()
    for snap in snapshots:
        all_keys.update(snap.env_a.keys())
        all_keys.update(snap.env_b.keys())

    # Build a value timeline per key: one entry per snapshot
    # We use env_b as the "current" state of each snapshot
    key_timeline: Dict[str, List[Optional[str]]] = {
        k: [] for k in all_keys
    }
    for snap in snapshots:
        for k in all_keys:
            # prefer env_b (the "after" side), fall back to env_a
            val = snap.env_b.get(k, snap.env_a.get(k))
            key_timeline[k].append(val)

    entries: List[HeatmapEntry] = []
    for key, values in key_timeline.items():
        changes = sum(
            1
            for i in range(1, len(values))
            if values[i] != values[i - 1]
        )
        last_val = values[-1] if values else None
        entries.append(
            HeatmapEntry(
                key=key,
                change_count=changes,
                total_snapshots=len(snapshots),
                last_value=last_val,
            )
        )

    entries.sort(key=lambda e: (-e.change_count, e.key))
    return HeatmapResult(entries=entries, snapshot_count=len(snapshots))
