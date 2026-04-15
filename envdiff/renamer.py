"""Rename keys across a parsed env dict, with conflict detection."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameConflict:
    old_key: str
    new_key: str
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"RenameConflict({self.old_key!r} -> {self.new_key!r}: {self.reason})"


@dataclass
class RenameResult:
    env: Dict[str, str]
    renamed: List[tuple]          # list of (old_key, new_key)
    skipped: List[RenameConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.skipped)

    @property
    def rename_count(self) -> int:
        return len(self.renamed)


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> RenameResult:
    """Return a new env dict with keys renamed according to *mapping*.

    Args:
        env:       Original key/value pairs.
        mapping:   {old_key: new_key} rename instructions.
        overwrite: If True, silently overwrite an existing key with the
                   same name as *new_key*.  Default is False (skip + record
                   a conflict instead).
    """
    result: Dict[str, str] = dict(env)
    renamed: List[tuple] = []
    skipped: List[RenameConflict] = []

    for old_key, new_key in mapping.items():
        if old_key not in result:
            skipped.append(
                RenameConflict(old_key, new_key, "source key not found")
            )
            continue

        if new_key in result and not overwrite:
            skipped.append(
                RenameConflict(old_key, new_key, f"target key '{new_key}' already exists")
            )
            continue

        value = result.pop(old_key)
        result[new_key] = value
        renamed.append((old_key, new_key))

    return RenameResult(env=result, renamed=renamed, skipped=skipped)
