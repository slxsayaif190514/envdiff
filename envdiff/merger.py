"""Merge multiple .env files into a unified view with conflict tracking."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeConflict:
    key: str
    values: Dict[str, Optional[str]]  # filename -> value

    def __repr__(self) -> str:
        parts = ", ".join(f"{f}={v!r}" for f, v in self.values.items())
        return f"MergeConflict(key={self.key!r}, [{parts}])"


@dataclass
class MergeResult:
    merged: Dict[str, Optional[str]] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    @property
    def conflict_keys(self) -> List[str]:
        return [c.key for c in self.conflicts]


def merge_envs(
    envs: List[Tuple[str, Dict[str, Optional[str]]]],
    strategy: str = "first",
) -> MergeResult:
    """Merge a list of (filename, env_dict) pairs.

    strategy:
      'first'  — keep the first file's value on conflict
      'last'   — keep the last file's value on conflict
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    result = MergeResult(sources=[name for name, _ in envs])
    conflict_map: Dict[str, Dict[str, Optional[str]]] = {}

    for filename, env in envs:
        for key, value in env.items():
            if key not in result.merged:
                result.merged[key] = value
                conflict_map[key] = {filename: value}
            else:
                existing_value = result.merged[key]
                conflict_map[key][filename] = value
                if value != existing_value:
                    if strategy == "last":
                        result.merged[key] = value

    for key, file_values in conflict_map.items():
        if len(file_values) > 1:
            unique_vals = set(file_values.values())
            if len(unique_vals) > 1:
                result.conflicts.append(MergeConflict(key=key, values=file_values))

    return result
