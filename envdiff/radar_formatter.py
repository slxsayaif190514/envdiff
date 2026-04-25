"""Formatter for RadarResult."""
from __future__ import annotations
from envdiff.differ_radar import RadarResult


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


def _bar(score: float, width: int = 20) -> str:
    filled = round(score * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _color_score(score: float, s: str) -> str:
    if score >= 0.9:
        return _green(s)
    if score >= 0.6:
        return _yellow(s)
    return _red(s)


def format_radar_result(result: RadarResult, *, no_color: bool = False) -> str:
    def c(fn, s):
        return s if no_color else fn(s)

    lines = []
    lines.append(c(_bold, f"Radar Comparison: {result.file_a}  vs  {result.file_b}"))
    lines.append(c(_dim, "-" * 60))

    col_w = 16
    header = f"  {'Axis':<{col_w}}  {'File A':>8}  {'File B':>8}  {'Delta':>8}  Bar (A)"
    lines.append(c(_bold, header))
    lines.append(c(_dim, "-" * 60))

    for ax in result.axes:
        bar = _bar(ax.score_a)
        delta_str = f"{ax.delta:+.2f}"
        sa_str = f"{ax.score_a:.2f}"
        sb_str = f"{ax.score_b:.2f}"

        if not no_color:
            sa_str = _color_score(ax.score_a, sa_str)
            sb_str = _color_score(ax.score_b, sb_str)
            delta_str = _green(delta_str) if ax.delta >= 0 else _red(delta_str)
            bar = _cyan(bar)

        lines.append(f"  {ax.name:<{col_w}}  {sa_str:>8}  {sb_str:>8}  {delta_str:>8}  {bar}")

    lines.append(c(_dim, "-" * 60))
    oa = f"{result.overall_a:.2f}"
    ob = f"{result.overall_b:.2f}"
    if not no_color:
        oa = _color_score(result.overall_a, oa)
        ob = _color_score(result.overall_b, ob)
    lines.append(f"  {'Overall':<{col_w}}  {oa:>8}  {ob:>8}")
    return "\n".join(lines)
