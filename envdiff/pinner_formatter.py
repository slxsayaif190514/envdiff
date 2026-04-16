"""Format PinResult for terminal output."""
from __future__ import annotations

from envdiff.pinner import PinResult


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


def format_pin_result(result: PinResult, *, color: bool = True) -> str:
    def c(fn, s):
        return fn(s) if color else s

    lines = [c(_bold, f"Pin check: {result.filename}")]

    if result.is_clean:
        lines.append(c(_green, "  ✔ No drift detected"))
        lines.append(c(_dim, f"  {len(result.entries)} key(s) match pinned values"))
        return "\n".join(lines)

    lines.append(c(_red, f"  ✘ {result.drift_count} drifted key(s) found"))
    for entry in result.entries:
        if not entry.drifted:
            continue
        if entry.current_value is None:
            lines.append(
                c(_yellow, f"  - {entry.key}") + c(_dim, f"  (removed, was {entry.pinned_value!r})")
            )
        else:
            lines.append(
                c(_yellow, f"  ~ {entry.key}")
                + c(_dim, f"  pinned={entry.pinned_value!r} current={entry.current_value!r}")
            )
    return "\n".join(lines)
