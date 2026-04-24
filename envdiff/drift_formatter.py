"""Format DriftResult for terminal output."""

from __future__ import annotations

from envdiff.differ_drift import DriftResult


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


def format_drift_result(result: DriftResult, *, color: bool = True) -> str:
    def b(s: str) -> str:
        return _bold(s) if color else s

    def g(s: str) -> str:
        return _green(s) if color else s

    def r(s: str) -> str:
        return _red(s) if color else s

    def y(s: str) -> str:
        return _yellow(s) if color else s

    def d(s: str) -> str:
        return _dim(s) if color else s

    lines: list[str] = []
    header = b(f"Drift: {result.source_label}  →  {result.target_label}")
    lines.append(header)
    lines.append(d("-" * 50))

    if result.is_clean:
        lines.append(g("✓ No drift detected"))
        return "\n".join(lines)

    for entry in result.by_type("added"):
        lines.append(g(f"  + {entry.key}") + d(f"  = {entry.new_value!r}"))

    for entry in result.by_type("removed"):
        lines.append(r(f"  - {entry.key}") + d(f"  was {entry.old_value!r}"))

    for entry in result.by_type("changed"):
        lines.append(y(f"  ~ {entry.key}"))
        lines.append(d(f"      before: {entry.old_value!r}"))
        lines.append(d(f"      after:  {entry.new_value!r}"))

    lines.append(d("-" * 50))
    summary_parts = []
    added = len(result.by_type("added"))
    removed = len(result.by_type("removed"))
    changed = len(result.by_type("changed"))
    if added:
        summary_parts.append(g(f"{added} added"))
    if removed:
        summary_parts.append(r(f"{removed} removed"))
    if changed:
        summary_parts.append(y(f"{changed} changed"))
    lines.append(b("Summary: ") + ", ".join(summary_parts))

    return "\n".join(lines)
