"""Human-readable formatter for EnvProfile objects."""
from __future__ import annotations

from envdiff.profiler import EnvProfile


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def _cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m"


def format_profile(profile: EnvProfile, *, color: bool = True) -> str:
    """Return a formatted string summarising *profile*."""
    b = _bold if color else str
    c = _cyan if color else str
    y = _yellow if color else str
    d = _dim if color else str

    lines: list[str] = []
    lines.append(b(f"Profile: {profile.filename}"))
    lines.append(f"  Total keys   : {c(str(profile.total_keys))}")

    if profile.is_empty:
        lines.append(d("  (no keys found)"))
        return "\n".join(lines)

    lines.append(f"  Empty values : {y(str(len(profile.empty_values)))}")
    if profile.empty_values:
        lines.append("    " + ", ".join(profile.empty_values))

    lines.append(f"  Booleans     : {len(profile.boolean_values)}")
    lines.append(f"  Numerics     : {len(profile.numeric_values)}")
    lines.append(f"  URLs         : {len(profile.url_values)}")
    lines.append(f"  Long values  : {len(profile.long_values)}")
    if profile.long_values:
        lines.append("    " + ", ".join(profile.long_values))

    if profile.prefixes:
        lines.append("  Key prefixes :")
        for prefix, count in sorted(profile.prefixes.items(), key=lambda x: -x[1]):
            lines.append(f"    {prefix}_*  -> {count} key(s)")

    return "\n".join(lines)
