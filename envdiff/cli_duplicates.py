"""CLI sub-command: envdiff duplicates <file>"""
from __future__ import annotations

import sys
from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path

from .duplicator import find_duplicates
from .duplicator_formatter import format_duplicate_result


def add_duplicates_subparser(subparsers: _SubParsersAction) -> None:  # type: ignore[type-arg]
    p: ArgumentParser = subparsers.add_parser(
        "duplicates",
        help="detect duplicate keys in a .env file",
    )
    p.add_argument("file", help="path to the .env file to scan")
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="disable ANSI colour output",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="exit with code 1 when duplicates are found",
    )
    p.set_defaults(func=_run_duplicates)


def _run_duplicates(args) -> None:  # type: ignore[no-untyped-def]
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    result = find_duplicates(path)
    print(format_duplicate_result(result, color=not args.no_color))

    if args.exit_code and not result.is_clean:
        sys.exit(1)
