"""Format DuplicateResult for terminal output."""
from __future__ import annotations

from .duplicator import DuplicateResult


def _bold(t: str) -> str:
    return f"\033[1m{t}\033[0m"


def _red(t: str) -> str:
    return f"\033[31m{t}\033[0m"


def _yellow(t: str) -> str:
    return f"\033[33m{t}\033[0m"


def _green(t: str) -> str:
    return f"\033[32m{t}\033[0m"


def _dim(t: str) -> str:
    return f"\033[2m{t}\033[0m"


def format_duplicate_result(result: DuplicateResult, *, color: bool = True) -> str:
    def c(fn, t):  # noqa: ANN001
        return fn(t) if color else t

    lines = []
    header = f"Duplicate key scan: {result.filename}"
    lines.append(c(_bold, header))
    lines.append("")

    if result.is_clean:
        lines.append(c(_green, "  ✔ No duplicate keys found."))
        return "\n".join(lines)

    lines.append(
        f"  Found {c(_bold, str(result.duplicate_count))} duplicate key(s), "
        f"{c(_bold, str(result.conflict_count))} with value conflicts."
    )
    lines.append("")

    for dup in result.duplicates:
        tag = c(_red, "[conflict]") if dup.value_conflict else c(_yellow, "[duplicate]")
        lines.append(f"  {c(_bold, dup.key)}  {tag}")
        for lineno, val in zip(dup.lines, dup.values):
            lines.append(f"    {c(_dim, f'line {lineno}:')}  {val!r}")

    return "\n".join(lines)
