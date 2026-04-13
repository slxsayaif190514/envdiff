"""CLI subcommand: envdiff merge — merge multiple .env files."""

import argparse
import sys
from typing import List

from envdiff.merger import merge_envs
from envdiff.merger_formatter import format_merge_result
from envdiff.parser import EnvParseError, parse_env_file


def add_merge_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "merge",
        help="Merge multiple .env files and report conflicts",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to merge",
    )
    parser.add_argument(
        "--strategy",
        choices=["first", "last"],
        default="first",
        help="Conflict resolution strategy (default: first)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.set_defaults(func=_run_merge)


def _run_merge(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("error: merge requires at least two files", file=sys.stderr)
        return 2

    envs = []
    for path in args.files:
        try:
            parsed = parse_env_file(path)
            envs.append((path, parsed))
        except EnvParseError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    result = merge_envs(envs, strategy=args.strategy)
    output = format_merge_result(result, no_color=args.no_color)
    print(output)
    return 1 if result.has_conflicts else 0
