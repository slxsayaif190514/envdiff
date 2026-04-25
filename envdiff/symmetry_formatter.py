"""Formatter for SymmetryResult."""
from __future__ import annotations
from envdiff.differ_symmetry import SymmetryResult


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


def format_symmetry_result(result: SymmetryResult, *, color: bool = True) -> str:
    def c(fn, s):
        return fn(s) if color else s

    pct = result.symmetry_ratio * 100
    lines = [
        c(_bold, f"Symmetry Report: {result.file_a}  vs  {result.file_b}"),
        c(_dim, "-" * 50),
        f"  Total unique keys : {result.total_keys}",
        f"  Shared keys       : {len(result.shared_keys)}",
        f"  Only in {result.file_a:<12}: {len(result.exclusive_a)}",
        f"  Only in {result.file_b:<12}: {len(result.exclusive_b)}",
        f"  Symmetry ratio    : {c(_green if result.is_symmetric else _yellow, f'{pct:.1f}%')}",
        "",
    ]

    if result.exclusive_a:
        lines.append(c(_bold, f"Only in {result.file_a}:"))
        for e in result.exclusive_a:
            lines.append(f"  {c(_yellow, e.key)}")
        lines.append("")

    if result.exclusive_b:
        lines.append(c(_bold, f"Only in {result.file_b}:"))
        for e in result.exclusive_b:
            lines.append(f"  {c(_yellow, e.key)}")
        lines.append("")

    if result.is_symmetric:
        lines.append(c(_green, "✔ Files are fully symmetric."))
    else:
        lines.append(c(_red, "✘ Files are not fully symmetric."))

    return "\n".join(lines)
