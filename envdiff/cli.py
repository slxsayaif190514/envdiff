"""CLI entry point for envdiff."""

import sys
import argparse

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare
from envdiff.formatter import format_result
from envdiff.reporter import build_summary, format_summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    p.add_argument("file_a", help="First .env file (baseline)")
    p.add_argument("file_b", help="Second .env file (target)")
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a summary report after the diff",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_a = parse_env_file(args.file_a)
    except (EnvParseError, OSError) as exc:
        print(f"envdiff: error reading {args.file_a}: {exc}", file=sys.stderr)
        return 1

    try:
        env_b = parse_env_file(args.file_b)
    except (EnvParseError, OSError) as exc:
        print(f"envdiff: error reading {args.file_b}: {exc}", file=sys.stderr)
        return 1

    result = compare(env_a, env_b)

    color = not args.no_color
    output = format_result(result, color=color)
    if output:
        print(output)

    if args.summary:
        summary = build_summary(result, args.file_a, args.file_b)
        print()
        print(format_summary(summary))

    return 1 if result.has_differences else 0


if __name__ == "__main__":
    sys.exit(main())
