"""Cluster env keys by value similarity into groups."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ClusterEntry:
    value: str
    keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ClusterEntry(value={self.value!r}, keys={self.keys})"


@dataclass
class ClusterResult:
    filename: str
    clusters: List[ClusterEntry] = field(default_factory=list)

    @property
    def cluster_count(self) -> int:
        return len(self.clusters)

    @property
    def total_keys(self) -> int:
        return sum(len(c.keys) for c in self.clusters)

    @property
    def singleton_count(self) -> int:
        """Clusters with only one key (unique values)."""
        return sum(1 for c in self.clusters if len(c.keys) == 1)

    @property
    def shared_count(self) -> int:
        """Clusters where multiple keys share the same value."""
        return sum(1 for c in self.clusters if len(c.keys) > 1)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ClusterResult(filename={self.filename!r}, "
            f"clusters={self.cluster_count}, total_keys={self.total_keys})"
        )


def cluster_env(env: Dict[str, str], filename: str = "") -> ClusterResult:
    """Group keys by identical value."""
    value_map: Dict[str, List[str]] = {}
    for key, value in sorted(env.items()):
        value_map.setdefault(value, []).append(key)

    clusters = [
        ClusterEntry(value=v, keys=sorted(keys))
        for v, keys in sorted(value_map.items())
    ]
    return ClusterResult(filename=filename, clusters=clusters)
