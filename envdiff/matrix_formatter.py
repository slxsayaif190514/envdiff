"""Formatter for MatrixResult."""
from __future__ import annotations
from envdiff.differ_matrix import MatrixResult, MatrixCell


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


def _fmt_cell(cell: MatrixCell) -> str:
    header = _bold(f"{cell.file_a}  vs  {cell.file_b}")
    if not cell.has_issues:
        return f"  {header}  {_green('✔ no differences')}"
    parts = [f"  {header}  {_red(str(cell.issue_count) + ' issue(s)')}"]  
    if cell.result.missing_in_b:
        keys = ", ".join(d.key for d in cell.result.missing_in_b)
        parts.append(f"    {_yellow('missing in b')}: {keys}")
    if cell.result.missing_in_a:
        keys = ", ".join(d.key for d in cell.result.missing_in_a)
        parts.append(f"    {_yellow('missing in a')}: {keys}")
    if cell.result.mismatches:
        keys = ", ".join(d.key for d in cell.result.mismatches)
        parts.append(f"    {_yellow('mismatches')}: {keys}")
    return "\n".join(parts)


def format_matrix_result(result: MatrixResult) -> str:
    lines = [_bold(f"Env Matrix — {len(result.files)} file(s), {result.pair_count} pair(s)")]
    if not result.cells:
        lines.append(_dim("  No pairs to compare."))
        return "\n".join(lines)
    for cell in result.cells:
        lines.append(_fmt_cell(cell))
    summary = f"  {_green(str(len(result.clean_pairs)) + ' clean')}, {_red(str(len(result.dirty_pairs)) + ' with issues')}"
    lines.append(summary)
    return "\n".join(lines)
