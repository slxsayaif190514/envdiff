"""Compute and compare digest (hash) fingerprints for .env files."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DigestEntry:
    key: str
    value_hash: str
    raw_value: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"DigestEntry({self.key!r}, hash={self.value_hash[:8]}...)"


@dataclass
class DigestResult:
    filename: str
    entries: Dict[str, DigestEntry] = field(default_factory=dict)
    file_hash: str = ""

    @property
    def key_count(self) -> int:
        return len(self.entries)

    def get(self, key: str) -> Optional[DigestEntry]:
        return self.entries.get(key)


def _hash_value(value: str) -> str:
    """Return a short SHA-256 hex digest for a value string."""
    return hashlib.sha256(value.encode()).hexdigest()


def _hash_file(env: Dict[str, str]) -> str:
    """Return a deterministic hash of the entire env mapping."""
    combined = ";".join(f"{k}={v}" for k, v in sorted(env.items()))
    return hashlib.sha256(combined.encode()).hexdigest()


def digest_env(filename: str, env: Dict[str, str]) -> DigestResult:
    """Build a DigestResult from a parsed env mapping."""
    entries = {
        key: DigestEntry(key=key, value_hash=_hash_value(value), raw_value=value)
        for key, value in env.items()
    }
    return DigestResult(
        filename=filename,
        entries=entries,
        file_hash=_hash_file(env),
    )


def compare_digests(a: DigestResult, b: DigestResult) -> Dict[str, str]:
    """Return a dict of keys whose value hashes differ between a and b.

    Keys present in only one result are also included with status
    'only_in_a' or 'only_in_b'.
    """
    all_keys = set(a.entries) | set(b.entries)
    diffs: Dict[str, str] = {}
    for key in sorted(all_keys):
        in_a = key in a.entries
        in_b = key in b.entries
        if in_a and not in_b:
            diffs[key] = "only_in_a"
        elif in_b and not in_a:
            diffs[key] = "only_in_b"
        elif a.entries[key].value_hash != b.entries[key].value_hash:
            diffs[key] = "changed"
    return diffs
