"""Deduplicates keys across multiple env dicts, keeping a chosen strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class DedupeEntry:
    key: str
    kept_value: str
    kept_source: str
    duplicates: List[Tuple[str, str]]  # (source, value) pairs that were dropped

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DedupeEntry(key={self.key!r}, kept_source={self.kept_source!r}, "
            f"dropped={len(self.duplicates)})"
        )


@dataclass
class DedupeResult:
    filename: str
    entries: List[DedupeEntry] = field(default_factory=list)
    clean_env: Dict[str, str] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return len(self.entries) == 0

    @property
    def dedupe_count(self) -> int:
        return sum(len(e.duplicates) for e in self.entries)

    @property
    def affected_keys(self) -> List[str]:
        return [e.key for e in self.entries]


def deduplicate_env(
    sources: List[Tuple[str, Dict[str, str]]],
    strategy: str = "first",
    label: Optional[str] = None,
) -> DedupeResult:
    """Merge multiple env dicts, resolving duplicate keys by strategy.

    Args:
        sources: list of (source_name, env_dict) pairs.
        strategy: 'first' keeps the first occurrence, 'last' keeps the last.
        label: optional label for the result filename field.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}; expected 'first' or 'last'")

    seen: Dict[str, List[Tuple[str, str]]] = {}
    for source_name, env in sources:
        for key, value in env.items():
            seen.setdefault(key, []).append((source_name, value))

    entries: List[DedupeEntry] = []
    clean_env: Dict[str, str] = {}

    for key, occurrences in seen.items():
        if len(occurrences) == 1:
            clean_env[key] = occurrences[0][1]
            continue

        if strategy == "first":
            kept_source, kept_value = occurrences[0]
            dropped = occurrences[1:]
        else:
            kept_source, kept_value = occurrences[-1]
            dropped = occurrences[:-1]

        clean_env[key] = kept_value
        entries.append(
            DedupeEntry(
                key=key,
                kept_value=kept_value,
                kept_source=kept_source,
                duplicates=dropped,
            )
        )

    filename = label or ", ".join(s for s, _ in sources)
    return DedupeResult(filename=filename, entries=sorted(entries, key=lambda e: e.key), clean_env=clean_env)
