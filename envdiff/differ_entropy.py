"""Entropy analysis for .env files — measures value diversity and predictability."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EntropyEntry:
    key: str
    value: str
    entropy: float
    level: str  # 'low', 'medium', 'high'

    def __repr__(self) -> str:  # pragma: no cover
        return f"EntropyEntry({self.key!r}, entropy={self.entropy:.3f}, level={self.level!r})"


@dataclass
class EntropyResult:
    filename: str
    entries: List[EntropyEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def average_entropy(self) -> float:
        if not self.entries:
            return 0.0
        return sum(e.entropy for e in self.entries) / len(self.entries)

    @property
    def high_entropy_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.level == "high"]

    @property
    def low_entropy_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.level == "low"]


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy of a string in bits."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum(
        (c / length) * math.log2(c / length)
        for c in counts.values()
    )


def _entropy_level(entropy: float, value_len: int) -> str:
    if value_len == 0:
        return "low"
    if entropy >= 3.5 and value_len >= 12:
        return "high"
    if entropy >= 2.0:
        return "medium"
    return "low"


def analyse_entropy(filename: str, env: Dict[str, str]) -> EntropyResult:
    """Analyse the Shannon entropy of each value in an env mapping."""
    entries: List[EntropyEntry] = []
    for key, value in sorted(env.items()):
        h = _shannon_entropy(value)
        level = _entropy_level(h, len(value))
        entries.append(EntropyEntry(key=key, value=value, entropy=h, level=level))
    return EntropyResult(filename=filename, entries=entries)
