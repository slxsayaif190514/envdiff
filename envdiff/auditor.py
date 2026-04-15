"""Audit trail: track which keys changed between two env snapshots over time."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from envdiff.comparator import CompareResult, KeyDiff


@dataclass
class AuditEntry:
    key: str
    change_type: str  # 'added', 'removed', 'modified', 'unchanged'
    old_value: Optional[str]
    new_value: Optional[str]
    timestamp: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"AuditEntry({self.key!r}, {self.change_type!r})"


@dataclass
class AuditReport:
    file_a: str
    file_b: str
    generated_at: str
    entries: List[AuditEntry] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return all(e.change_type == "unchanged" for e in self.entries)

    @property
    def change_count(self) -> int:
        return sum(1 for e in self.entries if e.change_type != "unchanged")

    def by_type(self, change_type: str) -> List[AuditEntry]:
        return [e for e in self.entries if e.change_type == change_type]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit_diff(result: CompareResult, file_a: str = "", file_b: str = "") -> AuditReport:
    """Convert a CompareResult into a structured AuditReport."""
    ts = _now_iso()
    entries: List[AuditEntry] = []

    for diff in result.missing_in_b:
        entries.append(AuditEntry(diff.key, "removed", diff.value_a, None, ts))

    for diff in result.missing_in_a:
        entries.append(AuditEntry(diff.key, "added", None, diff.value_b, ts))

    for diff in result.mismatches:
        entries.append(AuditEntry(diff.key, "modified", diff.value_a, diff.value_b, ts))

    for diff in result.matches:
        entries.append(AuditEntry(diff.key, "unchanged", diff.value_a, diff.value_b, ts))

    entries.sort(key=lambda e: e.key)
    return AuditReport(file_a=file_a, file_b=file_b, generated_at=ts, entries=entries)
