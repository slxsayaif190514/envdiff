"""Tests for envdiff.auditor."""
from __future__ import annotations

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.auditor import audit_diff, AuditReport, AuditEntry


def _diff(key, va=None, vb=None):
    return KeyDiff(key=key, value_a=va, value_b=vb)


@pytest.fixture()
def empty_result():
    return CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[], matches=[])


@pytest.fixture()
def mixed_result():
    return CompareResult(
        missing_in_b=[_diff("REMOVED", va="old")],
        missing_in_a=[_diff("ADDED", vb="new")],
        mismatches=[_diff("CHANGED", va="v1", vb="v2")],
        matches=[_diff("SAME", va="x", vb="x")],
    )


def test_audit_clean_when_no_diffs(empty_result):
    report = audit_diff(empty_result)
    assert report.is_clean
    assert report.change_count == 0


def test_audit_entries_sorted_by_key(mixed_result):
    report = audit_diff(mixed_result)
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_added_entry(mixed_result):
    report = audit_diff(mixed_result)
    added = report.by_type("added")
    assert len(added) == 1
    assert added[0].key == "ADDED"
    assert added[0].new_value == "new"
    assert added[0].old_value is None


def test_removed_entry(mixed_result):
    report = audit_diff(mixed_result)
    removed = report.by_type("removed")
    assert len(removed) == 1
    assert removed[0].key == "REMOVED"
    assert removed[0].old_value == "old"
    assert removed[0].new_value is None


def test_modified_entry(mixed_result):
    report = audit_diff(mixed_result)
    modified = report.by_type("modified")
    assert len(modified) == 1
    assert modified[0].key == "CHANGED"
    assert modified[0].old_value == "v1"
    assert modified[0].new_value == "v2"


def test_unchanged_entry(mixed_result):
    report = audit_diff(mixed_result)
    unchanged = report.by_type("unchanged")
    assert len(unchanged) == 1
    assert unchanged[0].key == "SAME"


def test_change_count(mixed_result):
    report = audit_diff(mixed_result)
    assert report.change_count == 3  # added + removed + modified


def test_file_labels_stored():
    result = CompareResult([], [], [], [])
    report = audit_diff(result, file_a="a.env", file_b="b.env")
    assert report.file_a == "a.env"
    assert report.file_b == "b.env"


def test_generated_at_is_set(empty_result):
    report = audit_diff(empty_result)
    assert report.generated_at  # non-empty ISO timestamp
    assert "T" in report.generated_at


def test_not_clean_when_changes(mixed_result):
    report = audit_diff(mixed_result)
    assert not report.is_clean
