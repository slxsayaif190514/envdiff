"""Formatter for DiffStats output."""
from envdiff.differ_stats import DiffStats


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def format_stats(stats: DiffStats, *, color: bool = True) -> str:
    """Return a human-readable stats block."""
    lines = []

    header = "Diff Statistics"
    if stats.files:
        header += f" — {' vs '.join(stats.files)}"
    lines.append((_bold(header) if color else header))
    lines.append("-" * 40)

    def label(text: str, value: int, fn=None) -> str:
        val_str = str(value)
        if color and fn:
            val_str = fn(val_str)
        return f"  {text:<22} {val_str}"

    lines.append(label("Total keys:", stats.total_keys))
    lines.append(label("Matched:", stats.matched, _green if color else None))
    lines.append(label("Missing in A:", stats.missing_in_a, _yellow if stats.missing_in_a else _green))
    lines.append(label("Missing in B:", stats.missing_in_b, _yellow if stats.missing_in_b else _green))
    lines.append(label("Mismatched:", stats.mismatched, _red if stats.mismatched else _green))

    rate_str = f"{stats.match_rate}%"
    rate_colored = (_green(rate_str) if stats.match_rate == 100.0 else _yellow(rate_str)) if color else rate_str
    lines.append(f"  {'Match rate:':<22} {rate_colored}")

    lines.append("-" * 40)
    if stats.has_issues:
        summary = f"  {stats.issue_count} issue(s) found."
        lines.append(_red(summary) if color else summary)
    else:
        ok = "  All keys match."
        lines.append(_green(ok) if color else ok)

    return "\n".join(lines)
