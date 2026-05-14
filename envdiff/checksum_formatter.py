"""Formatter for ChecksumResult."""
from __future__ import annotations

from envdiff.differ_checksum import ChecksumResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_checksum_result(result: ChecksumResult, *, color: bool = True) -> str:
    def b(s: str) -> str:
        return _bold(s) if color else s

    def g(s: str) -> str:
        return _green(s) if color else s

    def r(s: str) -> str:
        return _red(s) if color else s

    def c(s: str) -> str:
        return _cyan(s) if color else s

    def d(s: str) -> str:
        return _dim(s) if color else s

    lines = []
    lines.append(b(f"Checksum Report — {result.file_count} file(s)"))
    lines.append("")

    for entry in result.entries:
        short = entry.checksum[:16]
        lines.append(
            f"  {c(entry.filename)}: {d(short + '...')}  "
            f"{d(str(entry.key_count) + ' keys')}"
        )

    lines.append("")
    if result.all_match:
        lines.append(g("✔ All checksums match."))
    else:
        lines.append(r("✘ Checksums differ — environments are not identical."))

    return "\n".join(lines)
