"""Detect duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class DuplicateEntry:
    key: str
    lines: List[int]  # 1-based line numbers where key appears
    values: List[str]  # corresponding values

    def __repr__(self) -> str:  # pragma: no cover
        return f"DuplicateEntry({self.key!r}, lines={self.lines})"

    @property
    def value_conflict(self) -> bool:
        """True when the duplicate entries have different values."""
        return len(set(self.values)) > 1


@dataclass
class DuplicateResult:
    filename: str
    duplicates: List[DuplicateEntry] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.duplicates) == 0

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def conflict_count(self) -> int:
        return sum(1 for d in self.duplicates if d.value_conflict)


def find_duplicates(path: str | Path) -> DuplicateResult:
    """Scan *path* for duplicate keys and return a DuplicateResult."""
    path = Path(path)
    seen: Dict[str, List[tuple]] = {}  # key -> [(line_no, value), ...]

    with path.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            seen.setdefault(key, []).append((lineno, value))

    duplicates = [
        DuplicateEntry(
            key=k,
            lines=[t[0] for t in entries],
            values=[t[1] for t in entries],
        )
        for k, entries in seen.items()
        if len(entries) > 1
    ]
    duplicates.sort(key=lambda d: d.lines[0])
    return DuplicateResult(filename=str(path), duplicates=duplicates)
