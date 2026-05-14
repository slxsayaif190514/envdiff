"""Format VarianceResult for terminal output."""

from __future__ import annotations

from envdiff.differ_variance import VarianceResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_variance_result(result: VarianceResult, *, color: bool = True) -> str:
    bold = _bold if color else str
    cyan = _cyan if color else str
    green = _green if color else str
    yellow = _yellow if color else str
    dim = _dim if color else str

    lines: list[str] = []
    files_label = "  ".join(result.filenames)
    lines.append(bold(f"Variance report — {len(result.filenames)} files — {files_label}"))
    lines.append(f"  Keys analysed : {result.key_count}")
    lines.append(f"  Uniform       : {result.uniform_count}")
    lines.append(f"  Variant       : {result.variant_count}")
    lines.append("")

    if result.is_uniform:
        lines.append(green("  ✔ All shared keys have consistent values across envs."))
        return "\n".join(lines)

    lines.append(bold("  Variant keys:"))
    for entry in result.entries:
        if entry.is_uniform:
            continue
        lines.append(f"  {cyan(entry.key)}  ({entry.variance_count} distinct values)")
        for fname, val in entry.values.items():
            display = repr(val) if val is not None else dim("<missing>")
            lines.append(f"    {yellow(fname)}: {display}")

    return "\n".join(lines)
