"""Frequency analysis: how often each key appears across multiple env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class FrequencyEntry:
    key: str
    count: int
    total: int
    sources: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"FrequencyEntry(key={self.key!r}, count={self.count}, total={self.total})"

    @property
    def ratio(self) -> float:
        """Fraction of envs that contain this key."""
        if self.total == 0:
            return 0.0
        return self.count / self.total

    @property
    def is_universal(self) -> bool:
        return self.count == self.total

    @property
    def is_rare(self) -> bool:
        return self.ratio < 0.5


@dataclass
class FrequencyResult:
    filename: str
    entries: List[FrequencyEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def universal_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_universal]

    @property
    def rare_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_rare]

    def get(self, key: str) -> FrequencyEntry | None:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def analyze_frequency(
    envs: Sequence[Dict[str, str]],
    filenames: Sequence[str] | None = None,
    label: str = "<multi>",
) -> FrequencyResult:
    """Count how many env dicts contain each key."""
    total = len(envs)
    names = list(filenames) if filenames else [f"env{i}" for i in range(total)]
    if len(names) != total:
        raise ValueError("filenames length must match envs length")

    counts: Dict[str, List[str]] = {}
    for env, name in zip(envs, names):
        for key in env:
            counts.setdefault(key, []).append(name)

    entries = [
        FrequencyEntry(key=k, count=len(srcs), total=total, sources=srcs)
        for k, srcs in sorted(counts.items())
    ]
    return FrequencyResult(filename=label, entries=entries)
