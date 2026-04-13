"""High-level diff orchestration: parse two env files and return a CompareResult."""

from pathlib import Path
from typing import Optional

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare, CompareResult
from envdiff.filter import filter_by_prefix, filter_by_pattern, filter_by_type
from envdiff.sorter import sort_result, SortKey


class DiffError(Exception):
    """Raised when the diff pipeline encounters a fatal problem."""


def run_diff(
    path_a: str,
    path_b: str,
    *,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    only_type: Optional[str] = None,
    sort_by: SortKey = SortKey.KEY,
    reverse: bool = False,
) -> CompareResult:
    """Parse *path_a* and *path_b*, apply optional filters/sort, return result.

    Parameters
    ----------
    path_a, path_b:
        Paths to the two .env files to compare.
    prefix:
        If given, keep only keys that start with this prefix (case-insensitive).
    pattern:
        If given, keep only keys matching this glob-style pattern.
    only_type:
        If given, one of ``'missing_a'``, ``'missing_b'``, ``'mismatch'``.
    sort_by:
        ``SortKey`` enum value controlling sort order.
    reverse:
        Reverse the sort direction.
    """
    for path in (path_a, path_b):
        if not Path(path).exists():
            raise DiffError(f"File not found: {path}")

    try:
        env_a = parse_env_file(path_a)
    except EnvParseError as exc:
        raise DiffError(f"Failed to parse {path_a}: {exc}") from exc

    try:
        env_b = parse_env_file(path_b)
    except EnvParseError as exc:
        raise DiffError(f"Failed to parse {path_b}: {exc}") from exc

    result = compare(env_a, env_b)

    if prefix:
        result = filter_by_prefix(result, prefix)
    if pattern:
        result = filter_by_pattern(result, pattern)
    if only_type:
        result = filter_by_type(result, only_type)

    result = sort_result(result, sort_by, reverse=reverse)
    return result
