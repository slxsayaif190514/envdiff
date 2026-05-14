"""Formatter for ScopeCompareResult."""
from __future__ import annotations
from envdiff.differ_scope import ScopeCompareResult


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


def format_scope_compare(result: ScopeCompareResult) -> str:
    lines = [
        _bold(f"Scope Compare: {result.scope_name}"),
        _dim(f"  {result.file_a}  vs  {result.file_b}"),
        "",
    ]

    if result.in_scope:
        lines.append(_cyan(f"In-scope keys ({len(result.in_scope)}):"))
        for e in result.in_scope:
            if e.value_a is None:
                lines.append(f"  {_yellow(e.key)}  {_dim('only in b:')} {e.value_b}")
            elif e.value_b is None:
                lines.append(f"  {_yellow(e.key)}  {_dim('only in a:')} {e.value_a}")
            elif e.value_a == e.value_b:
                lines.append(f"  {_green(e.key)}  {_dim(repr(e.value_a))}")
            else:
                lines.append(
                    f"  {_red(e.key)}  {_dim(repr(e.value_a))} -> {_dim(repr(e.value_b))}"
                )
        lines.append("")

    if result.out_of_scope:
        lines.append(_dim(f"Out-of-scope keys ({len(result.out_of_scope)}):"))
        for e in result.out_of_scope:
            lines.append(_dim(f"  {e.key}"))
        lines.append("")

    lines.append(
        f"  matches: {_green(str(result.match_count))}  "
        f"mismatches: {_red(str(result.mismatch_count))}"
    )
    return "\n".join(lines)
