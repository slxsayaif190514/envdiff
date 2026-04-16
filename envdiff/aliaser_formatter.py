"""Formatter for AliasResult output."""
from __future__ import annotations
from .aliaser import AliasResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_alias_result(result: AliasResult, *, color: bool = True) -> str:
    bold = _bold if color else str
    green = _green if color else str
    red = _red if color else str
    yellow = _yellow if color else str
    dim = _dim if color else str

    label = result.source_file or "<env>"
    lines = [bold(f"Alias report: {label}")]

    if not result.entries:
        lines.append(dim("  No aliases defined."))
        return "\n".join(lines)

    for entry in result.entries:
        arrow = f"{entry.old_key} -> {entry.new_key}"
        if entry.found:
            lines.append(green(f"  ✔  {arrow}") + dim(f"  (value: {entry.value!r})"))
        else:
            lines.append(red(f"  ✘  {arrow}") + yellow("  [old key not found]"))

    total = len(result.entries)
    resolved = result.resolved_count
    missing = result.missing_count

    lines.append("")
    summary = f"  {resolved}/{total} aliases resolved"
    if missing:
        lines.append(yellow(summary) + red(f"  ({missing} missing)"))
    else:
        lines.append(green(summary))

    return "\n".join(lines)
