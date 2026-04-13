"""Format MergeResult for terminal output."""

from typing import Optional
from envdiff.merger import MergeResult
from envdiff.formatter import _bold, _green, _red, _yellow


def format_merge_result(result: MergeResult, no_color: bool = False) -> str:
    """Return a human-readable string describing the merge result."""

    def bold(s: str) -> str:
        return s if no_color else _bold(s)

    def green(s: str) -> str:
        return s if no_color else _green(s)

    def red(s: str) -> str:
        return s if no_color else _red(s)

    def yellow(s: str) -> str:
        return s if no_color else _yellow(s)

    lines = []
    sources_str = ", ".join(result.sources)
    lines.append(bold(f"Merged {len(result.sources)} file(s): {sources_str}"))
    lines.append(f"Total keys: {len(result.merged)}")

    if not result.has_conflicts:
        lines.append(green("No conflicts found."))
        return "\n".join(lines)

    lines.append(red(f"{len(result.conflicts)} conflict(s) detected:"))
    lines.append("")

    for conflict in sorted(result.conflicts, key=lambda c: c.key):
        lines.append(bold(f"  {conflict.key}"))
        for filename, value in conflict.values.items():
            display = repr(value) if value is not None else "(missing)"
            lines.append(yellow(f"    {filename}: {display}"))

    return "\n".join(lines)
