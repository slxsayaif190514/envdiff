"""Profile an env file: count keys, detect patterns, summarize value types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class EnvProfile:
    filename: str
    total_keys: int
    empty_values: List[str] = field(default_factory=list)
    numeric_values: List[str] = field(default_factory=list)
    boolean_values: List[str] = field(default_factory=list)
    url_values: List[str] = field(default_factory=list)
    long_values: List[str] = field(default_factory=list)  # values > 100 chars
    prefixes: Dict[str, int] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return self.total_keys == 0


_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}


def _detect_prefix(key: str) -> str | None:
    """Return the prefix (up to first underscore) if one exists."""
    if "_" in key:
        return key.split("_", 1)[0]
    return None


def profile_env_file(path: str) -> EnvProfile:
    """Parse *path* and return an EnvProfile describing its contents."""
    env = parse_env_file(path)
    profile = EnvProfile(filename=path, total_keys=len(env))

    for key, value in env.items():
        if value == "":
            profile.empty_values.append(key)
        elif value.lower() in _BOOL_VALUES:
            profile.boolean_values.append(key)
        elif value.lstrip("-").replace(".", "", 1).isdigit():
            profile.numeric_values.append(key)
        elif value.startswith(("http://", "https://", "ftp://")):
            profile.url_values.append(key)

        if len(value) > 100:
            profile.long_values.append(key)

        prefix = _detect_prefix(key)
        if prefix:
            profile.prefixes[prefix] = profile.prefixes.get(prefix, 0) + 1

    return profile
