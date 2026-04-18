"""Mask sensitive values in env dicts for safe display or export."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_FRAGMENTS = (
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "private", "auth", "credential", "cert", "signing",
)

MASK = "***"


@dataclass
class MaskResult:
    filename: str
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)

    @property
    def is_clean(self) -> bool:
        return self.mask_count == 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"MaskResult(file={self.filename!r}, masked={self.mask_count})"


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def mask_env(env: Dict[str, str], filename: str = "") -> MaskResult:
    """Return a MaskResult with sensitive values replaced by MASK."""
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key):
            masked[key] = MASK
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(
        filename=filename,
        original=dict(env),
        masked=masked,
        masked_keys=sorted(masked_keys),
    )
