"""CLI entry point for envdiff."""

import argparse
import sys

from envdiff.comparator import compare
from envdiff.exporter import export_result
from envdiff.filter import filter_by_prefix, filter_by_pattern, filter_by_type
from envdiff.formatter import format_result
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.reporter import build_summary, format_summary
from envdiff.sorter import SortKey, sort_result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files and highlight missing or mismatched keys.",
    )
    p.add_argument("file_a", help="First .env file (reference)")
    p.add_argument("file_b", help="Second .env file (target)")
    p.add_argument("--prefix", help="Only compare keys with this prefix")
    p.add_argument("--pattern", help="Only compare keys matching this glob pattern")
    p.add_argument(
        "--type",
        dest="diff_type",
        choices=["missing_in_b", "missing_in_a", "mismatch"],
        help="Only show diffs of this type",
    )
    p.add_argument(
        "--sort",
        choices=[s.value for s in SortKey],
        default=SortKey.KEY.value,
        help="Sort results by this field (default: key)",
    )
    p.add_argument("--reverse", action="store_true", help="Reverse sort order")
    p.add_argument(
        "--export",
        choices=["json", "csv"],
        help="Export results in the given format instead of printing",
    )
    p.add_argument("--output", help="Output file path for --export (default: stdout)")
    p.add_argument("--summary", action="store_true", help="Print a summary line at the end")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"envdiff: {exc}", file=sys.stderr)
        return 1

    result = compare(env_a, env_b)

    if args.prefix:
        result = filter_by_prefix(result, args.prefix)
    if args.pattern:
        result = filter_by_pattern(result, args.pattern)
    if args.diff_type:
        result = filter_by_type(result, args.diff_type)

    result = sort_result(result, by=SortKey(args.sort), reverse=args.reverse)

    if args.export:
        output = export_result(result, fmt=args.export)
        if args.output:
            with open(args.output, "w") as fh:
                fh.write(output)
        else:
            print(output)
        return 0

    color = not args.no_color
    print(format_result(result, color=color))

    if args.summary:
        summary = build_summary(args.file_a, args.file_b, result)
        print(format_summary(summary))

    return 1 if (result.missing_in_b or result.missing_in_a or result.mismatches) else 0


if __name__ == "__main__":
    sys.exit(main())
