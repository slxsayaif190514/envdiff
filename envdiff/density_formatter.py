"""Format DensityResult for terminal output."""
from __future__ import annotations

from envdiff.differ_density import DensityResult


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


def format_density_result(result: DensityResult) -> str:
    lines: list[str] = []
    label = result.filename or "<env>"
    lines.append(_bold(f"Density report: {label}"))
    lines.append(
        f"  Keys: {result.key_count}  "
        f"Avg length: {result.average_length:.1f}  "
        f"Empty: {result.empty_count}  "
        f"Short: {result.short_count}  "
        f"Long: {result.long_count}"
    )
    lines.append("")

    if not result.entries:
        lines.append(_dim("  (no keys)"))
        return "\n".join(lines)

    for entry in result.entries:
        if entry.is_empty:
            tag = _yellow("[empty]")
        elif entry.is_long:
            tag = _cyan("[long]")
        elif entry.is_short:
            tag = _dim("[short]")
        else:
            tag = _green("[ok]")
        lines.append(f"  {entry.key:<32} len={entry.length:<6} {tag}")

    return "\n".join(lines)
