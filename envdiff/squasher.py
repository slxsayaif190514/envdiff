"""Squash multiple env dicts into one, tracking which keys were dropped or kept."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SquashEntry:
    key: str
    value: str
    sources: List[str]  # env labels where this key appeared
    dropped_values: List[Tuple[str, str]]  # (source, value) that were overridden

    def __repr__(self) -> str:
        return f"SquashEntry(key={self.key!r}, value={self.value!r}, sources={self.sources})"


@dataclass
class SquashResult:
    filename: str
    entries: List[SquashEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def dropped_count(self) -> int:
        return sum(len(e.dropped_values) for e in self.entries)

    @property
    def is_clean(self) -> bool:
        return self.dropped_count == 0

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]


def squash_envs(
    envs: List[Tuple[str, Dict[str, str]]],
    strategy: str = "last",
) -> SquashResult:
    """Squash a list of (label, env_dict) pairs into a single SquashResult.

    strategy:
      'last'  — last value wins (default)
      'first' — first value wins
    """
    if not envs:
        return SquashResult(filename="<squashed>")

    accumulated: Dict[str, SquashEntry] = {}

    for label, env in envs:
        for key, value in env.items():
            if key not in accumulated:
                accumulated[key] = SquashEntry(
                    key=key,
                    value=value,
                    sources=[label],
                    dropped_values=[],
                )
            else:
                entry = accumulated[key]
                entry.sources.append(label)
                if strategy == "first":
                    entry.dropped_values.append((label, value))
                else:  # last
                    entry.dropped_values.append((entry.sources[-2], entry.value))
                    entry.value = value

    label_str = "+".join(lbl for lbl, _ in envs)
    result = SquashResult(filename=f"<squashed:{label_str}>")
    result.entries = sorted(accumulated.values(), key=lambda e: e.key)
    return result
