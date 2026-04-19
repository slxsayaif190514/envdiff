"""Split a single .env file into multiple files by key prefix."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SplitEntry:
    key: str
    value: str
    prefix: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"SplitEntry({self.key!r}, prefix={self.prefix!r})"


@dataclass
class SplitResult:
    source: str
    groups: Dict[str, List[SplitEntry]] = field(default_factory=dict)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values())

    def keys_for(self, prefix: str) -> List[str]:
        return [e.key for e in self.groups.get(prefix, [])]


def _extract_prefix(key: str, separator: str = "_") -> str:
    if separator in key:
        return key.split(separator, 1)[0].upper()
    return "__OTHER__"


def split_env(
    env: Dict[str, str],
    filename: str = "",
    separator: str = "_",
    prefixes: List[str] | None = None,
) -> SplitResult:
    result = SplitResult(source=filename)
    for key, value in env.items():
        prefix = _extract_prefix(key, separator)
        if prefixes is not None:
            if prefix not in [p.upper() for p in prefixes]:
                prefix = "__OTHER__"
        entry = SplitEntry(key=key, value=value, prefix=prefix)
        result.groups.setdefault(prefix, []).append(entry)
    return result


def to_env_dict(result: SplitResult, prefix: str) -> Dict[str, str]:
    return {e.key: e.value for e in result.groups.get(prefix, [])}
