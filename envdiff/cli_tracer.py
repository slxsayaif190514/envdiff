"""CLI subcommand: trace a key across multiple env files."""
import argparse
from envdiff.parser import parse_env_file
from envdiff.tracer import trace_key
from envdiff.tracer_formatter import format_trace_result


def add_tracer_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "trace",
        help="Trace where a key's value comes from across env files",
    )
    p.add_argument("key", help="Key to trace")
    p.add_argument("files", nargs="+", help="Env files in priority order (lowest to highest)")
    p.set_defaults(func=_run_trace)


def _run_trace(args: argparse.Namespace) -> int:
    envs = []
    sources = []
    for path in args.files:
        try:
            envs.append(parse_env_file(path))
            sources.append(path)
        except Exception as exc:
            print(f"Error reading {path}: {exc}")
            return 1

    result = trace_key(args.key, envs, sources)
    print(format_trace_result(result))
    return 0
