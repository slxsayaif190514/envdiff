from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlatEntry:
    key: str
    value: str
    source: str
    nested_path: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        path = ".".join(self.nested_path) if self.nested_path else self.key
        return f"FlatEntry({path}={self.value!r} from {self.source})"


@dataclass
class FlattenResult:
    filename: str
    entries: List[FlatEntry] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def nested_count(self) -> int:
        return sum(1 for e in self.entries if len(e.nested_path) > 1)

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}


def _split_key(key: str, separator: str) -> List[str]:
    parts = key.split(separator)
    return parts if len(parts) > 1 else [key]


def flatten_env(
    env: Dict[str, str],
    filename: str = "<env>",
    separator: str = "__",
) -> FlattenResult:
    """Flatten a dict of env vars, splitting keys by separator into nested paths."""
    result = FlattenResult(filename=filename)
    for key, value in env.items():
        path = _split_key(key, separator)
        entry = FlatEntry(
            key=key,
            value=value,
            source=filename,
            nested_path=path,
        )
        result.entries.append(entry)
    return result
