"""Formatter for KeyTimeline / TimelineResult output."""

from __future__ import annotations

from envdiff.differ_timeline import TimelineResult


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


def format_timeline(result: TimelineResult, *, color: bool = True) -> str:
    lines: list[str] = []

    total = len(result.timelines)
    unstable = len(result.unstable_keys)
    stable = len(result.stable_keys)

    header = f"Key Timeline  —  {total} keys tracked"
    lines.append(_bold(header) if color else header)
    lines.append(
        f"  stable: {stable}   unstable: {unstable}"
    )
    lines.append("")

    if not result.timelines:
        lines.append(_dim("  (no keys)") if color else "  (no keys)")
        return "\n".join(lines)

    for tl in result.timelines:
        stability = (
            (_green("stable") if color else "stable")
            if tl.is_stable
            else (_yellow(f"{tl.change_count} change(s)") if color else f"{tl.change_count} change(s)")
        )
        key_label = (_cyan(tl.key) if color else tl.key)
        lines.append(f"  {key_label}  [{stability}]")
        for entry in tl.entries:
            val_display = entry.value if entry.value is not None else _dim("<absent>") if color else "<absent>"
            label = _dim(entry.snapshot_label) if color else entry.snapshot_label
            lines.append(f"    {label}: {val_display}")

    return "\n".join(lines)
