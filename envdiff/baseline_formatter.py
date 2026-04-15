"""Formatter for BaselineResult."""

from __future__ import annotations

from envdiff.baseline import BaselineResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def format_baseline_result(result: BaselineResult, *, color: bool = True) -> str:
    def c(fn, s):  # noqa: ANN001
        return fn(s) if color else s

    lines: list[str] = []
    lines.append(
        c(_bold, f"Baseline comparison: {result.env_file or '(env)'} vs snapshot '{result.snapshot_label}'")
    )

    if result.is_clean:
        lines.append(c(_green, "  ✔ No changes from baseline."))
        return "\n".join(lines)

    lines.append(f"  {result.issue_count} change(s) detected.")

    if result.added:
        lines.append(c(_cyan, f"\n  Added ({len(result.added)}):"))
        for d in result.added:
            lines.append(c(_cyan, f"    + {d.key}={d.current_value!r}"))

    if result.removed:
        lines.append(c(_red, f"\n  Removed ({len(result.removed)}):"))
        for d in result.removed:
            lines.append(c(_red, f"    - {d.key}  (was {d.baseline_value!r})"))

    if result.changed:
        lines.append(c(_yellow, f"\n  Changed ({len(result.changed)}):"))
        for d in result.changed:
            lines.append(
                c(_yellow, f"    ~ {d.key}: {d.baseline_value!r} → {d.current_value!r}")
            )

    return "\n".join(lines)
