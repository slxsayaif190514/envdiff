"""Format CoverageResult for terminal output."""
from __future__ import annotations
from envdiff.differ_coverage import CoverageResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_coverage_result(result: CoverageResult, *, no_color: bool = False) -> str:
    if no_color:
        bold = cyan = green = yellow = red = dim = lambda s: s
    else:
        bold, cyan, green, yellow, red, dim = _bold, _cyan, _green, _yellow, _red, _dim

    lines = []
    files_label = ", ".join(result.filenames) if result.filenames else "(none)"
    lines.append(bold(f"Key Coverage Report — {files_label}"))
    lines.append(dim(f"  Files : {len(result.filenames)}  |  Unique keys : {result.key_count}"))
    avg_pct = round(result.average_coverage * 100, 1)
    lines.append(dim(f"  Average coverage : {avg_pct}%"))
    lines.append("")

    if not result.entries:
        lines.append(green("  No keys found."))
        return "\n".join(lines)

    for entry in result.entries:
        pct = round(entry.coverage_ratio * 100)
        if entry.is_universal:
            marker = green(f"[{pct:3d}%]")
        elif pct >= 50:
            marker = yellow(f"[{pct:3d}%]")
        else:
            marker = red(f"[{pct:3d}%]")

        tag = ""
        if entry.is_universal:
            tag = dim(" universal")
        elif entry.is_orphan:
            tag = dim(" orphan")

        absent_note = ""
        if entry.absent_in:
            absent_note = dim("  missing in: " + ", ".join(entry.absent_in))

        lines.append(f"  {marker} {cyan(entry.key)}{tag}{absent_note}")

    lines.append("")
    lines.append(dim(f"  Universal : {len(result.universal_keys)}  |  Orphans : {len(result.orphan_keys)}"))
    return "\n".join(lines)
