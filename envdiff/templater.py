"""Generate a .env.template file from one or more parsed env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    comment: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"TemplateEntry(key={self.key!r}, placeholder={self.placeholder!r})"


@dataclass
class TemplateResult:
    entries: List[TemplateEntry] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)

    @property
    def key_count(self) -> int:
        return len(self.entries)

    def to_lines(self) -> List[str]:
        """Render the template as lines suitable for writing to a file."""
        lines: List[str] = []
        for entry in sorted(self.entries, key=lambda e: e.key):
            if entry.comment:
                lines.append(f"# {entry.comment}")
            lines.append(f"{entry.key}={entry.placeholder}")
        return lines


def _make_placeholder(key: str, value: str) -> str:
    """Derive a human-friendly placeholder from the key name and existing value."""
    if value == "":
        return ""
    lower = key.lower()
    if any(token in lower for token in ("url", "uri", "host", "endpoint")):
        return "<url>"
    if any(token in lower for token in ("port",)):
        return "<port>"
    if any(token in lower for token in ("secret", "password", "passwd", "token", "key", "auth")):
        return "<secret>"
    if any(token in lower for token in ("path", "dir", "file")):
        return "<path>"
    if value.lower() in ("true", "false", "1", "0", "yes", "no"):
        return "<bool>"
    try:
        int(value)
        return "<int>"
    except ValueError:
        pass
    try:
        float(value)
        return "<float>"
    except ValueError:
        pass
    return "<value>"


def build_template(
    envs: Dict[str, Dict[str, str]],
    *,
    include_comments: bool = True,
) -> TemplateResult:
    """Build a TemplateResult from a mapping of filename -> parsed env dict."""
    merged: Dict[str, TemplateEntry] = {}

    for filename, env in envs.items():
        for key, value in env.items():
            if key not in merged:
                placeholder = _make_placeholder(key, value)
                comment = f"seen in {filename}" if include_comments else None
                merged[key] = TemplateEntry(key=key, placeholder=placeholder, comment=comment)

    return TemplateResult(
        entries=list(merged.values()),
        source_files=list(envs.keys()),
    )
