"""Formatter for AgeResult output."""

from __future__ import annotations

from envdiff.differ_age import AgeEntry, AgeResult


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


def _format_entry(entry: AgeEntry) -> str:
    days = entry.age_days
    age_str = f"{days:.1f}d" if days is not None else "n/a"
    snaps = f"(seen in {entry.snapshot_count} snapshots)"
    staleness = _yellow(" [STALE]") if entry.is_stale else ""
    return f"  {_cyan(entry.key):<30} age={age_str:<10} {_dim(snaps)}{staleness}"


def format_age_result(result: AgeResult, no_color: bool = False) -> str:
    lines = []
    header = _bold(f"Key Age Report — {result.filename}")
    lines.append(header)
    lines.append(_dim(f"  Total keys : {result.key_count}"))
    lines.append(_dim(f"  Stale keys : {result.stale_count}"))
    lines.append("")

    if result.key_count == 0:
        lines.append(_dim("  No keys found."))
    elif result.is_clean:
        lines.append(_green("  ✔ No stale keys detected."))
    else:
        lines.append(_yellow(f"  ⚠ {result.stale_count} stale key(s) detected:"))
        lines.append("")
        for entry in result.entries:
            lines.append(_format_entry(entry))

    output = "\n".join(lines)
    if no_color:
        import re
        output = re.sub(r"\033\[[0-9;]*m", "", output)
    return output
