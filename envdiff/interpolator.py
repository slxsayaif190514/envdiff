"""Detect and resolve variable interpolation references in .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationIssue:
    key: str
    ref: str
    resolved: Optional[str]

    def __repr__(self) -> str:  # pragma: no cover
        status = f"='{self.resolved}'" if self.resolved is not None else "UNRESOLVED"
        return f"InterpolationIssue({self.key!r} -> ${self.ref!r} {status})"


@dataclass
class InterpolationResult:
    source: Dict[str, str]
    resolved: Dict[str, str] = field(default_factory=dict)
    issues: List[InterpolationIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def unresolved_count(self) -> int:
        return sum(1 for i in self.issues if i.resolved is None)


def _refs_in_value(value: str) -> List[str]:
    """Return all variable reference names found in *value*."""
    refs: List[str] = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def _resolve_value(value: str, env: Dict[str, str]) -> str:
    """Substitute known references; leave unknown ones as-is."""
    def _sub(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return env.get(name, m.group(0))

    return _REF_RE.sub(_sub, value)


def interpolate_env(env: Dict[str, str]) -> InterpolationResult:
    """Resolve interpolation references within *env* and report issues."""
    resolved: Dict[str, str] = {}
    issues: List[InterpolationIssue] = []

    for key, value in env.items():
        refs = _refs_in_value(value)
        resolved_value = _resolve_value(value, env)
        resolved[key] = resolved_value

        for ref in refs:
            ref_value = env.get(ref)
            issues.append(InterpolationIssue(key=key, ref=ref, resolved=ref_value))

    return InterpolationResult(source=env, resolved=resolved, issues=issues)
