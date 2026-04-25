"""Format SignatureResult for terminal output."""
from __future__ import annotations

from envdiff.differ_signature import SignatureResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


_TYPE_COLORS = {
    "empty": "\033[31m",
    "bool": "\033[35m",
    "int": "\033[34m",
    "float": "\033[34m",
    "url": "\033[32m",
    "path": "\033[33m",
    "string": "\033[0m",
}


def _color_type(t: str) -> str:
    color = _TYPE_COLORS.get(t, "\033[0m")
    return f"{color}{t}\033[0m"


def format_signature(result: SignatureResult) -> str:
    lines: list[str] = []
    lines.append(_bold(f"Signature: {result.filename}"))
    lines.append(_dim(f"  file hash : {result.file_hash}"))
    lines.append(_dim(f"  keys      : {result.key_count}"))
    lines.append("")
    if not result.entries:
        lines.append(_dim("  (no keys)"))
        return "\n".join(lines)
    col = max(len(e.key) for e in result.entries)
    for entry in result.entries:
        key_str = _cyan(entry.key.ljust(col))
        type_str = _color_type(entry.value_type.ljust(7))
        hash_str = _dim(entry.value_hash)
        lines.append(f"  {key_str}  {type_str}  {hash_str}")
    return "\n".join(lines)


def format_signature_diff(a: SignatureResult, b: SignatureResult) -> str:
    """Show structural differences between two signatures."""
    lines: list[str] = []
    lines.append(_bold(f"Signature diff: {a.filename}  vs  {b.filename}"))
    same = a.file_hash == b.file_hash
    status = "\033[32mIDENTICAL\033[0m" if same else "\033[31mDIFFERS\033[0m"
    lines.append(f"  structure : {status}")
    all_keys = sorted(set(e.key for e in a.entries) | set(e.key for e in b.entries))
    changed = []
    for k in all_keys:
        ea = a.get(k)
        eb = b.get(k)
        if ea is None:
            changed.append(_yellow(f"  + {k} (only in {b.filename})"))
        elif eb is None:
            changed.append(_yellow(f"  - {k} (only in {a.filename})"))
        elif ea.value_type != eb.value_type:
            changed.append(_yellow(f"  ~ {k}: {ea.value_type} -> {eb.value_type}"))
    if changed:
        lines.append("")
        lines.extend(changed)
    return "\n".join(lines)
