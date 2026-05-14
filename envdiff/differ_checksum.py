"""Checksum comparison across multiple env files."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChecksumEntry:
    filename: str
    checksum: str
    key_count: int

    def __repr__(self) -> str:  # pragma: no cover
        return f"ChecksumEntry({self.filename!r}, {self.checksum[:8]}...)"


@dataclass
class ChecksumResult:
    entries: List[ChecksumEntry] = field(default_factory=list)
    _checksums: Dict[str, str] = field(default_factory=dict, repr=False)

    @property
    def file_count(self) -> int:
        return len(self.entries)

    @property
    def all_match(self) -> bool:
        if len(self.entries) < 2:
            return True
        values = {e.checksum for e in self.entries}
        return len(values) == 1

    def get(self, filename: str) -> Optional[ChecksumEntry]:
        for e in self.entries:
            if e.filename == filename:
                return e
        return None


def _checksum_env(env: Dict[str, str]) -> str:
    """Produce a stable SHA-256 digest for an env dict."""
    parts = []
    for key in sorted(env):
        parts.append(f"{key}={env[key]}")
    raw = "\n".join(parts).encode()
    return hashlib.sha256(raw).hexdigest()


def build_checksum_result(
    envs: List[Dict[str, str]],
    filenames: List[str],
) -> ChecksumResult:
    if len(envs) != len(filenames):
        raise ValueError("envs and filenames must have the same length")

    result = ChecksumResult()
    for env, filename in zip(envs, filenames):
        checksum = _checksum_env(env)
        entry = ChecksumEntry(
            filename=filename,
            checksum=checksum,
            key_count=len(env),
        )
        result.entries.append(entry)
    return result
