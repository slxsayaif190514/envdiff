"""CLI entry point for envdiff."""

import sys
from pathlib import Path

import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs
from envdiff.formatter import format_result


@click.command()
@click.argument("file_a", type=click.Path(exists=True, dir_okay=False))
@click.argument("file_b", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--keys-only",
    is_flag=True,
    default=False,
    help="Only check for missing keys, skip value comparison.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable colored output.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 if differences are found (useful in CI).",
)
def main(
    file_a: str,
    file_b: str,
    keys_only: bool,
    no_color: bool,
    exit_code: bool,
) -> None:
    """Compare two .env files and report differences."""
    path_a = Path(file_a)
    path_b = Path(file_b)

    try:
        env_a = parse_env_file(path_a)
    except EnvParseError as exc:
        click.echo(f"Error parsing {file_a}: {exc}", err=True)
        sys.exit(2)

    try:
        env_b = parse_env_file(path_b)
    except EnvParseError as exc:
        click.echo(f"Error parsing {file_b}: {exc}", err=True)
        sys.exit(2)

    result = compare_envs(
        env_a,
        env_b,
        env_a_name=path_a.name,
        env_b_name=path_b.name,
        keys_only=keys_only,
    )

    output = format_result(result, no_color=no_color)
    click.echo(output)

    if exit_code and result.has_differences:
        sys.exit(1)


if __name__ == "__main__":
    main()
