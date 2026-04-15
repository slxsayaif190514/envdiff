"""Format an AuditReport for terminal display."""
from __future__ import annotations

from envdiff.auditor import AuditReport


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_audit_report(report: AuditReport, plain: bool = False) -> str:
    def c(fn, s):
        return s if plain else fn(s)

    lines = []
    lines.append(c(_bold, f"Audit Report: {report.file_a} → {report.file_b}"))
    lines.append(c(_dim, f"Generated at: {report.generated_at}"))
    lines.append("")

    if report.is_clean:
        lines.append(c(_green, "✔ No changes detected."))
        return "\n".join(lines)

    added = report.by_type("added")
    removed = report.by_type("removed")
    modified = report.by_type("modified")

    if added:
        lines.append(c(_bold, f"Added ({len(added)}):"))
        for e in added:
            lines.append(c(_green, f"  + {e.key} = {e.new_value}"))

    if removed:
        lines.append(c(_bold, f"Removed ({len(removed)}):"))
        for e in removed:
            lines.append(c(_red, f"  - {e.key} = {e.old_value}"))

    if modified:
        lines.append(c(_bold, f"Modified ({len(modified)}):"))
        for e in modified:
            lines.append(c(_yellow, f"  ~ {e.key}: {e.old_value!r} → {e.new_value!r}"))

    lines.append("")
    lines.append(c(_cyan, f"Total changes: {report.change_count}"))
    return "\n".join(lines)
