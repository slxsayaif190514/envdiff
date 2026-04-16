"""Tag keys in env files with user-defined labels."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import fnmatch


@dataclass
class TagEntry:
    key: str
    tags: List[str]

    def __repr__(self) -> str:
        return f"TagEntry({self.key!r}, tags={self.tags})"


@dataclass
class TagResult:
    filename: str
    entries: List[TagEntry] = field(default_factory=list)
    untagged: List[str] = field(default_factory=list)

    @property
    def tagged_count(self) -> int:
        return len(self.entries)

    @property
    def is_fully_tagged(self) -> bool:
        return len(self.untagged) == 0


def _match_tags(key: str, rules: Dict[str, List[str]]) -> List[str]:
    matched: List[str] = []
    for pattern, tags in rules.items():
        if fnmatch.fnmatch(key, pattern):
            for t in tags:
                if t not in matched:
                    matched.append(t)
    return matched


def tag_env(
    env: Dict[str, str],
    rules: Dict[str, List[str]],
    filename: str = "",
) -> TagResult:
    """Apply tag rules to an env dict. Rules map glob patterns to tag lists."""
    entries: List[TagEntry] = []
    untagged: List[str] = []

    for key in sorted(env):
        tags = _match_tags(key, rules)
        if tags:
            entries.append(TagEntry(key=key, tags=tags))
        else:
            untagged.append(key)

    return TagResult(filename=filename, entries=entries, untagged=untagged)
