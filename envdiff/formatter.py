"""Output formatting for comparison results."""

from typing import Optional
from envdiff.comparator import CompareResult

TRY_COLORS = True
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    TRY_COLORS = False


def _red(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.RED}{text}{Style.RESET_ALL}"
    return text


def _yellow(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
    return text


def _green(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
    return text


def _bold(text: str) -> str:
    if TRY_COLORS:
        return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"
    return text


def format_result(result: CompareResult, no_color: bool = False) -> str:
    """Return a human-readable string summarizing the diff."""
    global TRY_COLORS
    if no_color:
        TRY_COLORS = False

    if not result.has_differences:
        return _green(f"✓ No differences between {result.env_a_name} and {result.env_b_name}")

    lines = [
        _bold(f"Comparing {result.env_a_name} ↔ {result.env_b_name}"),
        "",
    ]

    if result.missing_in_b:
        lines.append(_bold(f"Keys in {result.env_a_name} but missing in {result.env_b_name}:"))
        for diff in result.missing_in_b:
            lines.append(_red(f"  - {diff.key}"))
        lines.append("")

    if result.missing_in_a:
        lines.append(_bold(f"Keys in {result.env_b_name} but missing in {result.env_a_name}:"))
        for diff in result.missing_in_a:
            lines.append(_green(f"  + {diff.key}"))
        lines.append("")

    if result.mismatches:
        lines.append(_bold("Value mismatches:"))
        for diff in result.mismatches:
            lines.append(_yellow(f"  ~ {diff.key}"))
            lines.append(f"      {result.env_a_name}: {diff.env_a_value!r}")
            lines.append(f"      {result.env_b_name}: {diff.env_b_value!r}")
        lines.append("")

    total = len(result.diffs)
    lines.append(f"Total differences: {total}")
    return "\n".join(lines)
