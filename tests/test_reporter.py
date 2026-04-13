"""Tests for envdiff.reporter module."""

import pytest
from envdiff.comparator import CompareResult, KeyDiff
from envdiff.reporter import ReportSummary, build_summary, format_summary


def _make_result(missing_b=None, missing_a=None, mismatches=None, matched=0):
    diffs = []
    for key in (missing_b or []):
        diffs.append(KeyDiff(key=key, value_a="val", value_b=None))
    for key in (missing_a or []):
        diffs.append(KeyDiff(key=key, value_a=None, value_b="val"))
    for key in (mismatches or []):
        diffs.append(KeyDiff(key=key, value_a="x", value_b="y"))
    return CompareResult(diffs=diffs, matched_count=matched)


def test_summary_no_issues():
    result = _make_result(matched=5)
    summary = build_summary(result, ".env.dev", ".env.prod")
    assert summary.total_keys == 5
    assert summary.has_issues is False
    assert summary.issue_count == 0


def test_summary_missing_in_b():
    result = _make_result(missing_b=["DB_HOST", "DB_PORT"], matched=3)
    summary = build_summary(result, ".env.dev", ".env.prod")
    assert summary.missing_in_b == 2
    assert summary.missing_in_a == 0
    assert summary.mismatches == 0
    assert summary.has_issues is True
    assert summary.issue_count == 2


def test_summary_missing_in_a():
    result = _make_result(missing_a=["SECRET_KEY"], matched=2)
    summary = build_summary(result, "a", "b")
    assert summary.missing_in_a == 1
    assert summary.has_issues is True


def test_summary_mismatches():
    result = _make_result(mismatches=["API_URL", "LOG_LEVEL"], matched=1)
    summary = build_summary(result, "a", "b")
    assert summary.mismatches == 2
    assert summary.issue_count == 2


def test_summary_files_stored():
    result = _make_result(matched=1)
    summary = build_summary(result, ".env.staging", ".env.prod")
    assert summary.files == [".env.staging", ".env.prod"]


def test_format_summary_no_issues():
    summary = ReportSummary(total_keys=4, missing_in_b=0, missing_in_a=0,
                            mismatches=0, files=["a", "b"])
    text = format_summary(summary)
    assert "no issues found" in text.lower()
    assert "4" in text


def test_format_summary_with_issues():
    summary = ReportSummary(total_keys=6, missing_in_b=1, missing_in_a=2,
                            mismatches=1, files=["a", "b"])
    text = format_summary(summary)
    assert "4 issue(s)" in text
    assert "Comparing" in text
