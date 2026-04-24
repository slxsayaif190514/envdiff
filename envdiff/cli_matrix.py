"""CLI sub-command: matrix — compare multiple .env files pairwise."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.differ_matrix import build_matrix
from envdiff.matrix_formatter import format_matrix_result


def add_matrix_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "matrix",
        help="Compare multiple .env files pairwise and show a diff matrix.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI colour output.",
    )
    p.set_defaults(func=_run_matrix)


def _run_matrix(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("error: matrix requires at least 2 files.", file=sys.stderr)
        return 1

    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_env_file(path)
        except (EnvParseError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    result = build_matrix(envs)
    output = format_matrix_result(result)
    print(output)
    return 0 if not result.dirty_pairs else 1
