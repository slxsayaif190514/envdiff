"""Formatter for TagResult."""
from __future__ import annotations
from envdiff.tagger import TagResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def format_tag_result(result: TagResult, *, color: bool = True) -> str:
    b = _bold if color else str
    c = _cyan if color else str
    y = _yellow if color else str
    d = _dim if color else str
    g = _green if color else str

    lines = []
    label = result.filename or "<env>"
    lines.append(b(f"Tags for {label}"))
    lines.append(b(f"  Tagged keys : {result.tagged_count}"))
    lines.append(b(f"  Untagged    : {len(result.untagged)}"))
    lines.append("")

    if result.entries:
        lines.append(b("Tagged:"))
        for entry in result.entries:
            tag_str = ", ".join(c(t) for t in entry.tags)
            lines.append(f"  {entry.key}  {d('[')}{tag_str}{d(']')}")

    if result.untagged:
        lines.append("")
        lines.append(y("Untagged:"))
        for key in result.untagged:
            lines.append(f"  {d(key)}")

    if result.is_fully_tagged:
        lines.append("")
        lines.append(g("All keys are tagged."))

    return "\n".join(lines)
