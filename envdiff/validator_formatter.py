"""Format ValidationResult for terminal output."""
from __future__ import annotations

from envdiff.validator import ValidationResult


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def format_validation_result(result: ValidationResult, filename: str = "") -> str:
    label = f" for {filename}" if filename else ""
    lines: list[str] = []

    if result.is_valid:
        lines.append(_green(_bold(f"✔ Validation passed{label}.")))
        return "\n".join(lines)

    lines.append(_bold(f"Validation issues{label}: {result.issue_count} found"))

    if result.missing_required:
        lines.append(_red("  Missing required keys:"))
        for key in sorted(result.missing_required):
            lines.append(_red(f"    - {key}"))

    if result.unknown_keys:
        lines.append(_yellow("  Unknown keys (not in schema):"))
        for key in sorted(result.unknown_keys):
            lines.append(_yellow(f"    ~ {key}"))

    if result.type_errors:
        lines.append(_red("  Type validation errors:"))
        for key in sorted(result.type_errors):
            lines.append(_red(f"    {key}: {result.type_errors[key]}"))

    return "\n".join(lines)
