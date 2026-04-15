"""Format GroupResult for terminal output."""

from __future__ import annotations

from envdiff.grouper import GroupResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


_TYPE_SYMBOL = {
    "missing_in_b": _red("−"),
    "missing_in_a": _yellow("+"),
    "mismatch": _yellow("~"),
    "match": _dim("="),
}


def format_group_result(result: GroupResult, *, show_matches: bool = False) -> str:
    lines: list[str] = []
    lines.append(_bold(f"Key Groups ({len(result.groups)} groups, {result.total_keys} total keys)"))

    for name in result.group_names:
        group = result.groups[name]
        status = _red("issues") if group.has_issues else _dim("ok")
        lines.append(f"  {_cyan(name + '_*')}  [{status}]  {group.key_count} key(s)")
        for diff in sorted(group.diffs, key=lambda d: d.key):
            if diff.diff_type == "match" and not show_matches:
                continue
            symbol = _TYPE_SYMBOL.get(diff.diff_type, " ")
            lines.append(f"    {symbol} {diff.key}")

    if result.ungrouped:
        lines.append(f"  {_dim('(ungrouped)')}  {len(result.ungrouped)} key(s)")
        for diff in sorted(result.ungrouped, key=lambda d: d.key):
            if diff.diff_type == "match" and not show_matches:
                continue
            symbol = _TYPE_SYMBOL.get(diff.diff_type, " ")
            lines.append(f"    {symbol} {diff.key}")

    return "\n".join(lines)
