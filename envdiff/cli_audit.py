"""CLI subcommand: envdiff audit — show a structured audit of changes."""
from __future__ import annotations

import argparse
import sys

from envdiff.differ import run_diff, DiffError
from envdiff.auditor import audit_diff
from envdiff.auditor_formatter import format_audit_report


def add_audit_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "audit",
        help="show a structured audit trail of changes between two .env files",
    )
    p.add_argument("file_a", help="base .env file")
    p.add_argument("file_b", help="target .env file")
    p.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="disable ANSI colour output",
    )
    p.set_defaults(func=_run_audit)


def _run_audit(args: argparse.Namespace) -> int:
    try:
        result = run_diff(args.file_a, args.file_b)
    except DiffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    report = audit_diff(result, file_a=args.file_a, file_b=args.file_b)
    print(format_audit_report(report, plain=args.plain))
    return 0 if report.is_clean else 1
