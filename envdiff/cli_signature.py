"""CLI subcommand: envdiff signature"""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ_signature import sign_env
from envdiff.signature_formatter import format_signature, format_signature_diff


def add_signature_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "signature",
        help="show structural signature of one or two .env files",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to inspect")
    p.add_argument(
        "--diff",
        action="store_true",
        help="compare two files and show structural differences",
    )
    p.set_defaults(func=_run_signature)


def _run_signature(args: argparse.Namespace) -> int:
    if args.diff:
        if len(args.files) != 2:
            print("error: --diff requires exactly two files", file=sys.stderr)
            return 1
        try:
            env_a = parse_env_file(args.files[0])
            env_b = parse_env_file(args.files[1])
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        sig_a = sign_env(args.files[0], env_a)
        sig_b = sign_env(args.files[1], env_b)
        print(format_signature_diff(sig_a, sig_b))
        return 0

    for path in args.files:
        try:
            env = parse_env_file(path)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        sig = sign_env(path, env)
        print(format_signature(sig))
        if path != args.files[-1]:
            print()
    return 0
