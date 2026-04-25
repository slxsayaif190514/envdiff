"""CLI subcommand: symmetry — compare two env files for key symmetry."""
from __future__ import annotations
import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ_symmetry import compute_symmetry
from envdiff.symmetry_formatter import format_symmetry_result


def add_symmetry_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "symmetry",
        help="Analyse key symmetry between two .env files.",
    )
    p.add_argument("file_a", help="First .env file")
    p.add_argument("file_b", help="Second .env file")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when files are not symmetric",
    )
    p.set_defaults(func=_run_symmetry)


def _run_symmetry(args: argparse.Namespace) -> None:
    env_a = parse_env_file(args.file_a)
    env_b = parse_env_file(args.file_b)
    result = compute_symmetry(
        env_a, env_b, file_a=args.file_a, file_b=args.file_b
    )
    print(format_symmetry_result(result, color=not args.no_color))
    if args.exit_code and not result.is_symmetric:
        sys.exit(1)
