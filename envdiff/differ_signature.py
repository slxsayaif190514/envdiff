"""Compute and compare structural signatures for .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import hashlib
import json


@dataclass
class SignatureEntry:
    key: str
    value_type: str   # 'empty', 'int', 'bool', 'url', 'path', 'string'
    value_hash: str   # short sha256 of the raw value

    def __repr__(self) -> str:  # pragma: no cover
        return f"SignatureEntry({self.key!r}, {self.value_type}, {self.value_hash})"


@dataclass
class SignatureResult:
    filename: str
    entries: List[SignatureEntry] = field(default_factory=list)
    file_hash: str = ""

    @property
    def key_count(self) -> int:
        return len(self.entries)

    def get(self, key: str) -> SignatureEntry | None:
        for e in self.entries:
            if e.key == key:
                return e
        return None


def _value_type(value: str) -> str:
    if value == "":
        return "empty"
    if value.lower() in ("true", "false", "yes", "no", "1", "0"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if value.startswith(("http://", "https://")):
        return "url"
    if value.startswith("/") or value.startswith("./"):
        return "path"
    return "string"


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:8]


def sign_env(filename: str, env: Dict[str, str]) -> SignatureResult:
    """Build a SignatureResult from a parsed env dict."""
    entries = [
        SignatureEntry(key=k, value_type=_value_type(v), value_hash=_short_hash(v))
        for k, v in sorted(env.items())
    ]
    structure = json.dumps(
        {e.key: e.value_type for e in entries}, sort_keys=True
    )
    file_hash = _short_hash(structure)
    return SignatureResult(filename=filename, entries=entries, file_hash=file_hash)
