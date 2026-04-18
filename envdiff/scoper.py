"""Scope filtering: restrict env keys to a named scope defined by a mapping."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeEntry:
    key: str
    value: Optional[str]
    in_scope: bool

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScopeEntry({self.key!r}, in_scope={self.in_scope})"


@dataclass
class ScopeResult:
    filename: str
    scope_name: str
    entries: List[ScopeEntry] = field(default_factory=list)

    @property
    def in_scope_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.in_scope]

    @property
    def out_of_scope_keys(self) -> List[str]:
        return [e.key for e in self.entries if not e.in_scope]

    @property
    def in_scope_count(self) -> int:
        return len(self.in_scope_keys)

    @property
    def total_count(self) -> int:
        return len(self.entries)


def scope_env(
    env: Dict[str, str],
    scope_keys: List[str],
    scope_name: str = "default",
    filename: str = "",
) -> ScopeResult:
    """Tag each key in *env* as in-scope or out-of-scope based on *scope_keys*."""
    scope_set = set(scope_keys)
    entries = [
        ScopeEntry(key=k, value=v, in_scope=k in scope_set)
        for k, v in sorted(env.items())
    ]
    return ScopeResult(filename=filename, scope_name=scope_name, entries=entries)


def filter_to_scope(result: ScopeResult) -> Dict[str, Optional[str]]:
    """Return only the in-scope key/value pairs as a plain dict."""
    return {e.key: e.value for e in result.entries if e.in_scope}
