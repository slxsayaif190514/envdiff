"""Formats an OverlapResult for terminal output."""
from __future__ import annotations

from envdiff.differ_overlap import OverlapResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _pct(ratio: float) -> str:
    return f"{ratio * 100:.1f}%"


def format_overlap_result(res: OverlapResult) -> str:
    lines: list[str] = []
    lines.append(_bold(f"Key Overlap: {res.file_a}  vs  {res.file_b}"))
    lines.append("")

    lines.append(
        f"  {'Total unique keys':<28} {_cyan(str(res.total_unique_keys))}"
    )
    lines.append(
        f"  {'Shared keys':<28} {_cyan(str(len(res.shared_keys)))}  "
        f"{_dim('(overlap: ' + _pct(res.overlap_ratio) + ')')}"
    )
    lines.append(
        f"  {'Only in ' + res.file_a:<28} {_yellow(str(len(res.only_in_a)))}"
    )
    lines.append(
        f"  {'Only in ' + res.file_b:<28} {_yellow(str(len(res.only_in_b)))}"
    )
    lines.append("")
    lines.append(
        f"  {'Value matches (shared)':<28} {_green(str(len(res.value_matches)))}  "
        f"{_dim('(' + _pct(res.value_match_ratio) + ' of shared)')}"
    )
    lines.append(
        f"  {'Value mismatches (shared)':<28} {_red(str(len(res.value_mismatches)))}"
    )

    if res.only_in_a:
        lines.append("")
        lines.append(_bold(f"  Keys only in {res.file_a}:"))
        for k in sorted(res.only_in_a):
            lines.append(f"    {_yellow(k)}")

    if res.only_in_b:
        lines.append("")
        lines.append(_bold(f"  Keys only in {res.file_b}:"))
        for k in sorted(res.only_in_b):
            lines.append(f"    {_yellow(k)}")

    return "\n".join(lines)
