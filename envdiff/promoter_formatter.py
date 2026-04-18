from .promoter import PromoteResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def format_promote_result(result: PromoteResult) -> str:
    lines = []
    header = _bold(f"Promote: {result.source} → {result.target}")
    lines.append(header)
    lines.append("")

    if result.is_empty:
        lines.append(_green("  No keys promoted."))
    else:
        lines.append(_bold(f"  Promoted ({result.promote_count}):"))
        for entry in result.promoted:
            if entry.overwritten_value is not None:
                detail = (
                    f"  {_cyan(entry.key)} = {entry.value}"
                    f"  {_dim(f'(was: {entry.overwritten_value})')}"
                )
            else:
                detail = f"  {_cyan(entry.key)} = {entry.value}"
            lines.append(_green(f"  + {detail}"))

    if result.skipped:
        lines.append("")
        lines.append(_bold(f"  Skipped ({result.skip_count}):"))
        for key in result.skipped:
            lines.append(_yellow(f"  ~ {key}"))

    return "\n".join(lines)
