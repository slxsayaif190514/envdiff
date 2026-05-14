"""Scope comparison: identify which keys are in-scope vs out-of-scope across two env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeCompareEntry:
    key: str
    value_a: Optional[str]
    value_b: Optional[str]
    in_scope: bool

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScopeCompareEntry(key={self.key!r}, in_scope={self.in_scope})"


@dataclass
class ScopeCompareResult:
    file_a: str
    file_b: str
    scope_name: str
    entries: List[ScopeCompareEntry] = field(default_factory=list)

    @property
    def in_scope(self) -> List[ScopeCompareEntry]:
        return [e for e in self.entries if e.in_scope]

    @property
    def out_of_scope(self) -> List[ScopeCompareEntry]:
        return [e for e in self.entries if not e.in_scope]

    @property
    def match_count(self) -> int:
        return sum(
            1 for e in self.in_scope
            if e.value_a is not None and e.value_b is not None and e.value_a == e.value_b
        )

    @property
    def mismatch_count(self) -> int:
        return sum(
            1 for e in self.in_scope
            if e.value_a is not None and e.value_b is not None and e.value_a != e.value_b
        )


def build_scope_compare(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    scope_keys: List[str],
    file_a: str = "a",
    file_b: str = "b",
    scope_name: str = "default",
) -> ScopeCompareResult:
    all_keys = sorted(set(env_a) | set(env_b))
    scope_set = set(scope_keys)
    entries = [
        ScopeCompareEntry(
            key=k,
            value_a=env_a.get(k),
            value_b=env_b.get(k),
            in_scope=k in scope_set,
        )
        for k in all_keys
    ]
    return ScopeCompareResult(
        file_a=file_a,
        file_b=file_b,
        scope_name=scope_name,
        entries=entries,
    )
