"""Redact sensitive values in env dicts before display or export."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SENSITIVE_PATTERNS: List[re.Pattern] = [
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"passwd", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
    re.compile(r"auth", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
]

DEFAULT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)

    @property
    def is_clean(self) -> bool:
        return self.redact_count == 0


def _is_sensitive(key: str, extra_patterns: Optional[List[re.Pattern]] = None) -> bool:
    patterns = _SENSITIVE_PATTERNS + (extra_patterns or [])
    return any(p.search(key) for p in patterns)


def redact_env(
    env: Dict[str, str],
    placeholder: str = DEFAULT_PLACEHOLDER,
    extra_keys: Optional[List[str]] = None,
    extra_patterns: Optional[List[str]] = None,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by placeholder."""
    extra_key_set = set(extra_keys or [])
    compiled_extra = [
        re.compile(p, re.IGNORECASE) for p in (extra_patterns or [])
    ]

    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if key in extra_key_set or _is_sensitive(key, compiled_extra):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )
