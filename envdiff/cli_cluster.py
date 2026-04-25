"""CLI subcommand: cluster — group env keys by value similarity."""
from __future__ import annotations
import argparse
from envdiff.parser import parse_env_file
from envdiff.differ_cluster import cluster_env
from envdiff.cluster_formatter import format_cluster_result


def add_cluster_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "cluster",
        help="Group keys by identical value to find shared or duplicate values.",
    )
    p.add_argument("file", help="Path to .env file")
    p.add_argument(
        "--show-values",
        action="store_true",
        default=False,
        help="Include the actual value in the output (may expose secrets).",
    )
    p.add_argument(
        "--shared-only",
        action="store_true",
        default=False,
        help="Only show clusters where multiple keys share the same value.",
    )
    p.set_defaults(func=_run_cluster)


def _run_cluster(args: argparse.Namespace) -> None:
    env = parse_env_file(args.file)
    result = cluster_env(env, filename=args.file)

    if args.shared_only:
        result.clusters = [c for c in result.clusters if len(c.keys) > 1]

    print(format_cluster_result(result, show_values=args.show_values))

    if result.shared_count > 0:
        raise SystemExit(1)
