"""Compute key coverage across multiple env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CoverageEntry:
    key: str
    present_in: List[str]  # filenames where key exists
    absent_in: List[str]   # filenames where key is missing

    def __repr__(self) -> str:
        return (
            f"CoverageEntry(key={self.key!r}, "
            f"present={len(self.present_in)}, absent={len(self.absent_in)})"
        )

    @property
    def coverage_ratio(self) -> float:
        total = len(self.present_in) + len(self.absent_in)
        return len(self.present_in) / total if total else 1.0

    @property
    def is_universal(self) -> bool:
        return len(self.absent_in) == 0

    @property
    def is_orphan(self) -> bool:
        return len(self.present_in) == 1


@dataclass
class CoverageResult:
    filenames: List[str]
    entries: List[CoverageEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def universal_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_universal]

    @property
    def orphan_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.is_orphan]

    @property
    def average_coverage(self) -> float:
        if not self.entries:
            return 1.0
        return sum(e.coverage_ratio for e in self.entries) / len(self.entries)


def compute_coverage(envs: Dict[str, Dict[str, str]]) -> CoverageResult:
    """Given a mapping of filename -> env dict, compute per-key coverage."""
    filenames = list(envs.keys())
    all_keys: Set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())

    entries: List[CoverageEntry] = []
    for key in sorted(all_keys):
        present = [f for f, env in envs.items() if key in env]
        absent = [f for f in filenames if f not in present]
        entries.append(CoverageEntry(key=key, present_in=present, absent_in=absent))

    return CoverageResult(filenames=filenames, entries=entries)
