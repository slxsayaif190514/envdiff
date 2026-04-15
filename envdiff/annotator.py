"""Annotate a .env file with inline diff comments against a reference env."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import CompareResult


@dataclass
class AnnotatedLine:
    line_number: int
    raw: str
    key: Optional[str]
    annotation: Optional[str]  # None means no annotation
    tag: str = "ok"  # ok | missing_in_a | mismatch

    def __repr__(self) -> str:  # pragma: no cover
        return f"AnnotatedLine({self.line_number}, tag={self.tag!r}, annotation={self.annotation!r})"


@dataclass
class AnnotationResult:
    filename: str
    lines: List[AnnotatedLine] = field(default_factory=list)

    @property
    def has_annotations(self) -> bool:
        return any(ln.annotation is not None for ln in self.lines)

    @property
    def annotation_count(self) -> int:
        return sum(1 for ln in self.lines if ln.annotation is not None)


def annotate_env_file(
    filename: str,
    raw_lines: List[str],
    result: CompareResult,
) -> AnnotationResult:
    """Return an AnnotationResult where each line that corresponds to a
    key involved in a diff gets an inline comment explaining the issue."""

    missing_in_a: set = {d.key for d in result.missing_in_a}
    mismatches: Dict[str, str] = {d.key: d.value_b for d in result.mismatches}

    annotated: List[AnnotatedLine] = []
    for i, raw in enumerate(raw_lines, start=1):
        stripped = raw.strip()
        key: Optional[str] = None
        annotation: Optional[str] = None
        tag = "ok"

        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()

            if key in missing_in_a:
                annotation = f"# [envdiff] key not present in reference file"
                tag = "missing_in_a"
            elif key in mismatches:
                ref_val = mismatches[key]
                annotation = f"# [envdiff] value differs from reference (ref={ref_val!r})"
                tag = "mismatch"

        annotated.append(
            AnnotatedLine(
                line_number=i,
                raw=raw.rstrip("\n"),
                key=key,
                annotation=annotation,
                tag=tag,
            )
        )

    return AnnotationResult(filename=filename, lines=annotated)
