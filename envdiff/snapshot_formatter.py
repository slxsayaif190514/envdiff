"""Format a Snapshot for terminal display."""
from __future__ import annotations

from envdiff.snapshotter import Snapshot


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_snapshot(snap: Snapshot, *, color: bool = True) -> str:
    _b = _bold if color else str
    _c = _cyan if color else str
    _r = _red if color else str
    _y = _yellow if color else str
    _d = _dim if color else str

    lines: list[str] = []
    lines.append(_b(f"Snapshot: {snap.label}"))
    lines.append(_d(f"  Created : {snap.created_at}"))
    lines.append(_d(f"  File A  : {snap.file_a}"))
    lines.append(_d(f"  File B  : {snap.file_b}"))
    lines.append("")

    if not snap.diffs:
        lines.append("  No differences recorded.")
        return "\n".join(lines)

    lines.append(_b(f"  {len(snap.diffs)} difference(s):"))
    for diff in snap.diffs:
        tag = diff.diff_type
        if tag == "missing_in_b":
            lines.append(_r(f"  - [{tag}] {diff.key}") + _d(f"  (A={diff.value_a!r})"))
        elif tag == "missing_in_a":
            lines.append(_c(f"  + [{tag}] {diff.key}") + _d(f"  (B={diff.value_b!r})"))
        else:
            lines.append(
                _y(f"  ~ [{tag}] {diff.key}")
                + _d(f"  A={diff.value_a!r} → B={diff.value_b!r}")
            )

    return "\n".join(lines)
