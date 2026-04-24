"""Format DigestResult and compare_digests output for terminal display."""

from __future__ import annotations

from typing import Dict

from envdiff.digester import DigestResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_digest_result(result: DigestResult) -> str:
    lines = [
        _bold(f"Digest: {result.filename}"),
        _dim(f"  file hash : {result.file_hash[:16]}..."),
        _dim(f"  keys      : {result.key_count}"),
    ]
    for key, entry in sorted(result.entries.items()):
        lines.append(f"  {_cyan(key):<30} {_dim(entry.value_hash[:12])}...")
    return "\n".join(lines)


def format_digest_diff(
    a: DigestResult,
    b: DigestResult,
    diffs: Dict[str, str],
) -> str:
    header = _bold(f"Digest diff: {a.filename}  →  {b.filename}")
    if not diffs:
        return "\n".join([header, _green("  ✔ all value hashes match")])

    lines = [header]
    for key, status in sorted(diffs.items()):
        if status == "only_in_a":
            lines.append(f"  {_red('- ' + key):<32} {_dim('(only in ' + a.filename + ')')}")
        elif status == "only_in_b":
            lines.append(f"  {_yellow('+ ' + key):<32} {_dim('(only in ' + b.filename + ')')}")
        else:
            ha = a.entries[key].value_hash[:12] if key in a.entries else "—"
            hb = b.entries[key].value_hash[:12] if key in b.entries else "—"
            lines.append(
                f"  {_yellow('~ ' + key):<32} "
                f"{_dim(ha + '...')} → {_dim(hb + '...')}"
            )
    lines.append(_dim(f"  {len(diffs)} difference(s) found"))
    return "\n".join(lines)
