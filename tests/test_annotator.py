"""Tests for envdiff.annotator and envdiff.annotator_formatter."""

from __future__ import annotations

import pytest

from envdiff.annotator import annotate_env_file, AnnotationResult, AnnotatedLine
from envdiff.annotator_formatter import format_annotation_result
from envdiff.comparator import CompareResult, KeyDiff


def _make_result(
    missing_in_b=None,
    missing_in_a=None,
    mismatches=None,
) -> CompareResult:
    return CompareResult(
        missing_in_b=missing_in_b or [],
        missing_in_a=missing_in_a or [],
        mismatches=mismatches or [],
    )


RAW_LINES = [
    "APP_ENV=production\n",
    "DB_HOST=localhost\n",
    "SECRET_KEY=abc123\n",
    "# a comment\n",
    "EMPTY_VAR=\n",
]


def test_annotate_clean_file():
    result = _make_result()
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    assert isinstance(ar, AnnotationResult)
    assert not ar.has_annotations
    assert ar.annotation_count == 0


def test_annotate_mismatch_key():
    diff = KeyDiff(key="DB_HOST", value_a="localhost", value_b="db.prod.example.com")
    result = _make_result(mismatches=[diff])
    ar = annotate_env_file("prod.env", RAW_LINES, result)

    mismatch_lines = [ln for ln in ar.lines if ln.tag == "mismatch"]
    assert len(mismatch_lines) == 1
    assert mismatch_lines[0].key == "DB_HOST"
    assert "ref=" in mismatch_lines[0].annotation


def test_annotate_missing_in_a_key():
    diff = KeyDiff(key="SECRET_KEY", value_a=None, value_b="abc123")
    result = _make_result(missing_in_a=[diff])
    ar = annotate_env_file("prod.env", RAW_LINES, result)

    extra_lines = [ln for ln in ar.lines if ln.tag == "missing_in_a"]
    assert len(extra_lines) == 1
    assert extra_lines[0].key == "SECRET_KEY"
    assert "not present in reference" in extra_lines[0].annotation


def test_comment_lines_not_annotated():
    result = _make_result()
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    comment_lines = [ln for ln in ar.lines if ln.raw.strip().startswith("#")]
    assert all(ln.annotation is None for ln in comment_lines)


def test_line_numbers_are_correct():
    result = _make_result()
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    for i, ln in enumerate(ar.lines, start=1):
        assert ln.line_number == i


def test_annotation_count_matches_diffs():
    d1 = KeyDiff(key="DB_HOST", value_a="localhost", value_b="remote")
    d2 = KeyDiff(key="SECRET_KEY", value_a=None, value_b="abc123")
    result = _make_result(mismatches=[d1], missing_in_a=[d2])
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    assert ar.annotation_count == 2


def test_format_clean_result_no_color():
    result = _make_result()
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    output = format_annotation_result(ar, color=False)
    assert "No differences found" in output
    assert "prod.env" in output


def test_format_with_annotations_no_color():
    diff = KeyDiff(key="DB_HOST", value_a="localhost", value_b="remote")
    result = _make_result(mismatches=[diff])
    ar = annotate_env_file("prod.env", RAW_LINES, result)
    output = format_annotation_result(ar, color=False)
    assert "[envdiff]" in output
    assert "1 annotated line(s)" in output
