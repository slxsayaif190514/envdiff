"""Key aliasing: map old key names to new ones across env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasEntry:
    old_key: str
    new_key: str
    value: Optional[str]
    found: bool

    def __repr__(self) -> str:  # pragma: no cover
        status = "found" if self.found else "missing"
        return f"AliasEntry({self.old_key!r} -> {self.new_key!r}, {status})"


@dataclass
class AliasResult:
    source_file: str
    entries: List[AliasEntry] = field(default_factory=list)
    unmapped: Dict[str, str] = field(default_factory=dict)

    @property
    def resolved_count(self) -> int:
        return sum(1 for e in self.entries if e.found)

    @property
    def missing_count(self) -> int:
        return sum(1 for e in self.entries if not e.found)

    @property
    def is_clean(self) -> bool:
        return self.missing_count == 0

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Return env dict with old keys replaced by new keys."""
        result = dict(self.unmapped)
        for entry in self.entries:
            if entry.found:
                result[entry.new_key] = entry.value
        return result


def apply_aliases(
    env: Dict[str, str],
    aliases: Dict[str, str],
    source_file: str = "",
) -> AliasResult:
    """Apply a mapping of {old_key: new_key} to an env dict.

    Keys not in the alias map are passed through unchanged.
    If an old_key is not present in env, the entry is marked as missing.
    """
    alias_keys = set(aliases.keys())
    unmapped = {k: v for k, v in env.items() if k not in alias_keys}

    entries: List[AliasEntry] = []
    for old_key, new_key in sorted(aliases.items()):
        if old_key in env:
            entries.append(AliasEntry(old_key=old_key, new_key=new_key, value=env[old_key], found=True))
        else:
            entries.append(AliasEntry(old_key=old_key, new_key=new_key, value=None, found=False))

    return AliasResult(source_file=source_file, entries=entries, unmapped=unmapped)
