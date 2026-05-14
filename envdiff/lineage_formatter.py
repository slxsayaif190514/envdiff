"""Format LineageResult for terminal output."""

from __future__ import annotations

from envdiff.differ_lineage import LineageResult


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


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def format_lineage_result(result: LineageResult, no_color: bool = False) -> str:
    def c(fn, s):
        return s if no_color else fn(s)

    lines = []
    header = f"Key Lineage — {result.key_count} keys across {len(result.labels)} snapshots"
    lines.append(c(_bold, header))
    lines.append(c(_dim, "  Snapshots: " + ", ".join(result.labels)))
    lines.append("")

    unstable = set(result.unstable_keys)

    for key, entry in sorted(result.entries.items()):
        stability = c(_yellow, "~unstable") if key in unstable else c(_green, "stable")
        first = entry.first_seen or c(_dim, "never")
        last = entry.last_seen or c(_dim, "never")
        lines.append(
            f"  {c(_cyan, key)}  [{stability}]  "
            f"first={first}  last={last}  changes={entry.change_count}"
        )
        for event in entry.events:
            val_str = c(_dim, "<absent>") if event.value is None else repr(event.value)
            lines.append(f"      {c(_dim, event.snapshot_label)}: {val_str}")

    lines.append("")
    if unstable:
        lines.append(c(_yellow, f"  {len(unstable)} unstable key(s) detected."))
    else:
        lines.append(c(_green, "  All keys are stable across snapshots."))

    return "\n".join(lines)
