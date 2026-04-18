"""Trace where a key's value comes from across multiple env files."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TraceEntry:
    key: str
    source: str
    value: str
    overridden_by: Optional[str] = None

    def __repr__(self) -> str:
        return f"TraceEntry({self.key!r}, source={self.source!r}, value={self.value!r})"


@dataclass
class TraceResult:
    key: str
    entries: List[TraceEntry] = field(default_factory=list)

    @property
    def resolved_value(self) -> Optional[str]:
        active = [e for e in self.entries if e.overridden_by is None]
        return active[-1].value if active else None

    @property
    def resolved_source(self) -> Optional[str]:
        active = [e for e in self.entries if e.overridden_by is None]
        return active[-1].source if active else None

    @property
    def is_overridden(self) -> bool:
        return any(e.overridden_by is not None for e in self.entries)

    @property
    def source_count(self) -> int:
        return len(self.entries)


def trace_key(key: str, envs: List[Dict[str, str]], sources: List[str]) -> TraceResult:
    """Trace a key across ordered env dicts (later envs override earlier ones)."""
    if len(envs) != len(sources):
        raise ValueError("envs and sources must have the same length")

    result = TraceResult(key=key)
    last_seen_source: Optional[str] = None

    for env, source in zip(envs, sources):
        if key not in env:
            continue
        entry = TraceEntry(key=key, source=source, value=env[key])
        if result.entries:
            result.entries[-1].overridden_by = source
        result.entries.append(entry)
        last_seen_source = source

    return result
