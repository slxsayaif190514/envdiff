"""Cascade multiple .env files into a resolved environment, with override tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class CascadeEntry:
    key: str
    value: str
    source: str  # filename that provided the final value
    overridden_by: Optional[str] = None  # filename that overrode an earlier value

    def __repr__(self) -> str:
        return f"CascadeEntry({self.key!r}, source={self.source!r})"


@dataclass
class CascadeResult:
    sources: List[str]
    entries: List[CascadeEntry] = field(default_factory=list)
    override_count: int = 0

    @property
    def resolved(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    @property
    def key_count(self) -> int:
        return len(self.entries)

    @property
    def has_overrides(self) -> bool:
        return self.override_count > 0


def cascade_envs(envs: List[Tuple[str, Dict[str, str]]]) -> CascadeResult:
    """Merge a list of (filename, env_dict) pairs left-to-right, later files win."""
    if not envs:
        return CascadeResult(sources=[])

    sources = [name for name, _ in envs]
    result = CascadeResult(sources=sources)

    # Track current state: key -> (value, source)
    accumulated: Dict[str, Tuple[str, str]] = {}
    override_keys: Dict[str, str] = {}  # key -> overriding source

    for filename, env in envs:
        for key, value in env.items():
            if key in accumulated:
                prev_value, _ = accumulated[key]
                if prev_value != value:
                    result.override_count += 1
                    override_keys[key] = filename
            accumulated[key] = (value, filename)

    for key, (value, source) in sorted(accumulated.items()):
        entry = CascadeEntry(
            key=key,
            value=value,
            source=source,
            overridden_by=override_keys.get(key),
        )
        result.entries.append(entry)

    return result
