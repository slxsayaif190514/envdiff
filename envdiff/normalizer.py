"""Normalize .env values for consistent comparison."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeResult:
    filename: str
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)

    @property
    def is_clean(self) -> bool:
        return len(self.changes) == 0

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def __repr__(self) -> str:
        return f"NormalizeResult(file={self.filename!r}, changes={self.change_count})"


def _normalize_value(value: str) -> str:
    """Strip surrounding whitespace and normalize boolean-like values to lowercase."""
    value = value.strip()
    if value.lower() in ("true", "false", "yes", "no", "on", "off"):
        return value.lower()
    return value


def normalize_env(env: Dict[str, str], filename: str = "<env>") -> NormalizeResult:
    """Return a NormalizeResult with cleaned values and a record of what changed."""
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, original_value in env.items():
        new_value = _normalize_value(original_value)
        normalized[key] = new_value
        if new_value != original_value:
            changes.append((key, original_value, new_value))

    return NormalizeResult(
        filename=filename,
        original=dict(env),
        normalized=normalized,
        changes=changes,
    )
