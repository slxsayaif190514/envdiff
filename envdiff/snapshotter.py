"""Snapshot support: save and load env comparison states for later diffing."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from envdiff.comparator import CompareResult, KeyDiff


class SnapshotError(Exception):
    pass


@dataclass
class Snapshot:
    label: str
    created_at: str
    file_a: str
    file_b: str
    diffs: list[KeyDiff]

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "created_at": self.created_at,
            "file_a": self.file_a,
            "file_b": self.file_b,
            "diffs": [
                {
                    "key": d.key,
                    "type": d.diff_type,
                    "value_a": d.value_a,
                    "value_b": d.value_b,
                }
                for d in self.diffs
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Snapshot":
        diffs = [
            KeyDiff(
                key=d["key"],
                diff_type=d["type"],
                value_a=d["value_a"],
                value_b=d["value_b"],
            )
            for d in data.get("diffs", [])
        ]
        return cls(
            label=data["label"],
            created_at=data["created_at"],
            file_a=data["file_a"],
            file_b=data["file_b"],
            diffs=diffs,
        )


def save_snapshot(result: CompareResult, label: str, path: str) -> Snapshot:
    """Persist a CompareResult to a JSON snapshot file."""
    all_diffs = result.missing_in_b + result.missing_in_a + result.mismatches
    snap = Snapshot(
        label=label,
        created_at=datetime.now(timezone.utc).isoformat(),
        file_a=result.file_a,
        file_b=result.file_b,
        diffs=all_diffs,
    )
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(snap.to_dict(), fh, indent=2)
    except OSError as exc:
        raise SnapshotError(f"Cannot write snapshot to {path!r}: {exc}") from exc
    return snap


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot file not found: {path!r}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot from {path!r}: {exc}") from exc
    return Snapshot.from_dict(data)
