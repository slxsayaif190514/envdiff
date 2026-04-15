"""Format an AnnotationResult for terminal output."""

from __future__ import annotations

from envdiff.annotator import AnnotationResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_annotation_result(result: AnnotationResult, *, color: bool = True) -> str:
    lines: list[str] = []

    header = f"Annotations for {result.filename}"
    lines.append(_bold(header) if color else header)
    lines.append("")

    if not result.has_annotations:
        msg = "  No differences found — file matches reference."
        lines.append(_cyan(msg) if color else msg)
        return "\n".join(lines)

    for ln in result.lines:
        lineno = _dim(f"{ln.line_number:>4}: ") if color else f"{ln.line_number:>4}: "

        if ln.tag == "mismatch":
            body = _yellow(ln.raw) if color else ln.raw
        elif ln.tag == "missing_in_a":
            body = _red(ln.raw) if color else ln.raw
        else:
            body = ln.raw

        lines.append(f"{lineno}{body}")

        if ln.annotation:
            indent = "      "
            note = _dim(ln.annotation) if color else ln.annotation
            lines.append(f"{indent}{note}")

    lines.append("")
    summary = f"  {result.annotation_count} annotated line(s)."
    lines.append(_bold(summary) if color else summary)

    return "\n".join(lines)
