"""Formatter for FrequencyResult."""
from __future__ import annotations
from envdiff.differ_frequency import FrequencyResult


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


def format_frequency_result(result: FrequencyResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Key Frequency Analysis — {result.filename}  [{result.key_count} keys]"
    lines.append(_bold(header) if color else header)
    lines.append("")

    if not result.entries:
        msg = "  No keys found."
        lines.append(_dim(msg) if color else msg)
        return "\n".join(lines)

    for entry in result.entries:
        bar_len = int(entry.ratio * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        pct = f"{entry.ratio * 100:5.1f}%"
        src_str = _dim(f"  [{', '.join(entry.sources)}]") if color else f"  [{', '.join(entry.sources)}]"

        if entry.is_universal:
            key_str = _green(entry.key) if color else entry.key
            bar_str = _green(bar) if color else bar
        elif entry.is_rare:
            key_str = _yellow(entry.key) if color else entry.key
            bar_str = _yellow(bar) if color else bar
        else:
            key_str = _cyan(entry.key) if color else entry.key
            bar_str = _cyan(bar) if color else bar

        line = f"  {key_str:<30} {bar_str} {pct}  ({entry.count}/{entry.total}){src_str}"
        lines.append(line)

    lines.append("")
    univ = len(result.universal_keys)
    rare = len(result.rare_keys)
    summary = f"Universal: {univ}  |  Rare (<50%): {rare}  |  Total: {result.key_count}"
    lines.append(_bold(summary) if color else summary)
    return "\n".join(lines)
