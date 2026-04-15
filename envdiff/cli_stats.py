"""CLI subcommand: stats — show statistics for a diff between two env files."""
import argparse
import sys

from envdiff.differ import run_diff, DiffError
from envdiff.differ_stats import compute_stats
from envdiff.stats_formatter import format_stats


def add_stats_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "stats",
        help="Show key-level statistics for a diff between two .env files.",
    )
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any issues are found",
    )
    p.set_defaults(func=_run_stats)


def _run_stats(args: argparse.Namespace) -> int:
    try:
        result = run_diff(args.file_a, args.file_b)
    except DiffError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    stats = compute_stats(result, file_a=args.file_a, file_b=args.file_b)
    output = format_stats(stats, color=not args.no_color)
    print(output)

    if args.exit_code and stats.has_issues:
        return 1
    return 0
