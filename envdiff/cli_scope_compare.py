"""CLI subcommand: scope-compare — compare two env files within a named scope."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_env_file
from envdiff.differ_scope import build_scope_compare
from envdiff.scope_compare_formatter import format_scope_compare


def add_scope_compare_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "scope-compare",
        help="compare two env files restricted to a set of keys (scope)",
    )
    p.add_argument("file_a", help="first .env file")
    p.add_argument("file_b", help="second .env file")
    p.add_argument(
        "--scope",
        metavar="KEY",
        nargs="+",
        required=True,
        help="keys that define the scope",
    )
    p.add_argument("--scope-name", default="custom", help="label for the scope")
    p.set_defaults(func=_run_scope_compare)


def _run_scope_compare(args: argparse.Namespace) -> int:
    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = build_scope_compare(
        env_a=env_a,
        env_b=env_b,
        scope_keys=args.scope,
        file_a=args.file_a,
        file_b=args.file_b,
        scope_name=args.scope_name,
    )
    print(format_scope_compare(result))
    return 0 if result.mismatch_count == 0 else 1
