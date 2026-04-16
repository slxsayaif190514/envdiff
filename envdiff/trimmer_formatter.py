"""Format TrimResult for terminal output."""
from __future__ import annotations
from envdiff.trimmer import TrimResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_trim_result(result: TrimResult, *, color: bool = True) -> str:
    def c(fn, s):
        return fn(s) if color else s

    lines: list[str] = []
    header = f"Trim: {result.filename}" if result.filename else "Trim result"
    lines.append(c(_bold, header))

    if result.is_clean:
        lines.append(c(_green, "  No unused keys found."))
    else:
        lines.append(f"  Removed {c(_red, str(result.removed_count))} unused key(s):")
        for key in result.removed:
            lines.append(f"    {c(_red, '- ' + key)}")

    lines.append(c(_dim, f"  Kept {len(result.kept)} key(s)."))
    return "\n".join(lines)
