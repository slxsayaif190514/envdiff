"""Format TraceResult for CLI output."""
from envdiff.tracer import TraceResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_trace_result(result: TraceResult) -> str:
    lines = []
    lines.append(_bold(f"Trace: {result.key}"))

    if not result.entries:
        lines.append(_yellow(f"  Key '{result.key}' not found in any source."))
        return "\n".join(lines)

    for entry in result.entries:
        prefix = "  "
        value_str = _cyan(repr(entry.value))
        source_str = _bold(entry.source)
        if entry.overridden_by:
            lines.append(f"{prefix}{_dim(source_str)}  {_dim(value_str)}  {_dim(f'(overridden by {entry.overridden_by})')}")
        else:
            lines.append(f"{prefix}{source_str}  {value_str}  {_green('← resolved')}")

    lines.append("")
    lines.append(f"  Resolved value : {_green(repr(result.resolved_value))}")
    lines.append(f"  Resolved source: {_bold(result.resolved_source or '-')}")
    lines.append(f"  Sources checked: {result.source_count}")
    return "\n".join(lines)
