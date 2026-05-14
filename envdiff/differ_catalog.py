"""Build a catalog of all keys across multiple env files with metadata."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CatalogEntry:
    key: str
    sources: Dict[str, Optional[str]]  # filename -> value (None if absent)
    occurrence_count: int
    is_universal: bool

    def __repr__(self) -> str:
        return f"CatalogEntry(key={self.key!r}, occurrences={self.occurrence_count})"


@dataclass
class CatalogResult:
    filenames: List[str]
    entries: List[CatalogEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def universal_keys(self) -> List[CatalogEntry]:
        return [e for e in self.entries if e.is_universal]

    @property
    def partial_keys(self) -> List[CatalogEntry]:
        return [e for e in self.entries if not e.is_universal]

    def get(self, key: str) -> Optional[CatalogEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None


def build_catalog(envs: List[Dict[str, str]], filenames: List[str]) -> CatalogResult:
    """Build a catalog from a list of env dicts and their filenames."""
    if len(envs) != len(filenames):
        raise ValueError("envs and filenames must have the same length")

    all_keys: set = set()
    for env in envs:
        all_keys.update(env.keys())

    total = len(envs)
    entries: List[CatalogEntry] = []

    for key in sorted(all_keys):
        sources: Dict[str, Optional[str]] = {}
        count = 0
        for fname, env in zip(filenames, envs):
            val = env.get(key, None)
            sources[fname] = val
            if val is not None:
                count += 1
        entries.append(CatalogEntry(
            key=key,
            sources=sources,
            occurrence_count=count,
            is_universal=(count == total),
        ))

    return CatalogResult(filenames=list(filenames), entries=entries)
