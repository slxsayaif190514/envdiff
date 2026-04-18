"""Formatter for CascadeResult."""
from __future__ import annotations
from envdiff.cascader import CascadeResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_cascade_result(result: CascadeResult, no_color: bool = False) -> str:
    if no_color:
        bold = cyan = yellow = green = dim = lambda s: s
    else:
        bold, cyan, yellow, green, dim = _bold, _cyan, _yellow, _green, _dim

    lines: list[str] = []
    sources_str = " → ".join(result.sources)
    lines.append(bold(f"Cascade: {sources_str}"))
    lines.append(f"  Total keys : {result.key_count}")
    lines.append(f"  Overrides  : {result.override_count}")
    lines.append("")

    for entry in result.entries:
        source_label = dim(f"[{entry.source}]")
        if entry.overridden_by:
            tag = yellow(f" ↑ overridden by {entry.overridden_by}")
        else:
            tag = ""
        lines.append(f"  {cyan(entry.key)} = {entry.value}  {source_label}{tag}")

    if not result.entries:
        lines.append(green("  (no keys resolved)"))

    return "\n".join(lines)
