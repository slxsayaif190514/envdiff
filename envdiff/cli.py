"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare
from envdiff.exporter import export_result
from envdiff.filter import filter_by_prefix, filter_by_pattern
from envdiff.formatter import format_result
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.reporter import build_summary, format_summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    p.add_argument("file_a", type=Path, help="First .env file (reference)")
    p.add_argument("file_b", type=Path, help="Second .env file (target)")
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Only compare keys starting with PREFIX (case-insensitive)",
    )
    p.add_argument(
        "--pattern",
        metavar="PATTERN",
        help="Only compare keys matching shell-style wildcard PATTERN",
    )
    p.add_argument(
        "--export",
        choices=["json", "csv"],
        metavar="FORMAT",
        help="Export results in the given format (json or csv) instead of coloured text",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary after the diff output",
    )
    return p


def main(argv: list[str] | None = None) -> int:  # noqa: C901
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except (EnvParseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = compare(env_a, env_b)

    if args.prefix:
        result = filter_by_prefix(result, args.prefix)

    if args.pattern:
        result = filter_by_pattern(result, args.pattern)

    if args.export:
        print(export_result(result, args.export))
    else:
        print(format_result(result))

    if args.summary:
        summary = build_summary(result)
        print(format_summary(summary))

    has_diff = bool(
        result.missing_in_b or result.missing_in_a or result.mismatches
    )
    return 1 if has_diff else 0


if __name__ == "__main__":
    sys.exit(main())
