"""Trim unused or redundant keys from an env file given a reference set."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimResult:
    filename: str
    kept: Dict[str, str] = field(default_factory=dict)
    removed: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.removed) == 0

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TrimResult(kept={len(self.kept)}, removed={self.removed_count})"


def trim_env(
    env: Dict[str, str],
    reference: Dict[str, str],
    filename: str = "",
) -> TrimResult:
    """Remove keys from *env* that are not present in *reference*."""
    result = TrimResult(filename=filename)
    for key, value in env.items():
        if key in reference:
            result.kept[key] = value
        else:
            result.removed.append(key)
    result.removed.sort()
    return result
