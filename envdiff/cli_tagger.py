"""CLI subcommand: tag"""
from __future__ import annotations
import json
import sys
from argparse import ArgumentParser, Namespace
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.tagger import tag_env
from envdiff.tagger_formatter import format_tag_result


def add_tagger_subparser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "tag",
        help="Tag keys in an env file using pattern rules from a JSON rules file.",
    )
    p.add_argument("env_file", help="Path to the .env file")
    p.add_argument(
        "--rules",
        required=True,
        help="Path to a JSON file mapping glob patterns to tag lists",
    )
    p.add_argument("--no-color", action="store_true", help="Disable color output")
    p.set_defaults(func=_run_tag)


def _run_tag(args: Namespace) -> None:
    try:
        env = parse_env_file(args.env_file)
    except EnvParseError as exc:
        print(f"Error parsing env file: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.rules, "r", encoding="utf-8") as fh:
            rules = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error reading rules file: {exc}", file=sys.stderr)
        sys.exit(1)

    result = tag_env(env, rules, filename=args.env_file)
    print(format_tag_result(result, color=not args.no_color))
