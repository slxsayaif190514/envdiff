"""Format SplitResult for terminal output."""
from __future__ import annotations
from envdiff.splitter import SplitResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_split_result(result: SplitResult, no_color: bool = False) -> str:
    def b(s: str) -> str:
        return s if no_color else _bold(s)

    def c(s: str) -> str:
        return s if no_color else _cyan(s)

    def y(s: str) -> str:
        return s if no_color else _yellow(s)

    def d(s: str) -> str:
        return s if no_color else _dim(s)

    lines: list[str] = []
    header = f"Split result for {result.source}" if result.source else "Split result"
    lines.append(b(header))
    lines.append(f"  Groups : {result.group_count}")
    lines.append(f"  Total keys : {result.total_keys}")
    lines.append("")

    for prefix, entries in sorted(result.groups.items()):
        label = y(f"[{prefix}]") if prefix != "__OTHER__" else d("[__OTHER__]")
        lines.append(f"  {label}  ({len(entries)} keys)")
        for entry in sorted(entries, key=lambda e: e.key):
            lines.append(f"    {c(entry.key)} = {d(entry.value)}")

    return "\n".join(lines)
