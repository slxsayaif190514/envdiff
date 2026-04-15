"""Tests for envdiff.grouper."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.grouper import GroupResult, group_result, _extract_prefix


def _diff(key: str, diff_type: str) -> KeyDiff:
    return KeyDiff(key=key, value_a="x", value_b="y", diff_type=diff_type)


@pytest.fixture()
def mixed_result() -> CompareResult:
    return CompareResult(
        missing_in_b=[_diff("DB_HOST", "missing_in_b"), _diff("DB_PORT", "missing_in_b")],
        missing_in_a=[_diff("AWS_SECRET", "missing_in_a")],
        mismatches=[_diff("AWS_REGION", "mismatch")],
        matches=[_diff("APP_ENV", "match"), _diff("DEBUG", "match")],
    )


def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("DEBUG") is None


def test_extract_prefix_custom_separator():
    assert _extract_prefix("APP.NAME", separator=".") == "APP"


def test_group_result_creates_groups(mixed_result):
    gr = group_result(mixed_result)
    assert "DB" in gr.groups
    assert "AWS" in gr.groups
    assert "APP" in gr.groups


def test_group_result_ungrouped_no_prefix(mixed_result):
    gr = group_result(mixed_result)
    keys = [d.key for d in gr.ungrouped]
    assert "DEBUG" in keys


def test_group_key_count(mixed_result):
    gr = group_result(mixed_result)
    assert gr.groups["DB"].key_count == 2
    assert gr.groups["AWS"].key_count == 2


def test_group_has_issues_when_mismatch(mixed_result):
    gr = group_result(mixed_result)
    assert gr.groups["AWS"].has_issues is True


def test_group_no_issues_when_all_match():
    result = CompareResult(
        missing_in_b=[],
        missing_in_a=[],
        mismatches=[],
        matches=[_diff("APP_ENV", "match"), _diff("APP_NAME", "match")],
    )
    gr = group_result(result)
    assert gr.groups["APP"].has_issues is False


def test_total_keys(mixed_result):
    gr = group_result(mixed_result)
    assert gr.total_keys == 6


def test_group_names_sorted(mixed_result):
    gr = group_result(mixed_result)
    assert gr.group_names == sorted(gr.group_names)


def test_min_group_size_moves_small_groups_to_ungrouped():
    result = CompareResult(
        missing_in_b=[_diff("X_ONLY", "missing_in_b")],
        missing_in_a=[],
        mismatches=[],
        matches=[],
    )
    gr = group_result(result, min_group_size=2)
    assert "X" not in gr.groups
    assert any(d.key == "X_ONLY" for d in gr.ungrouped)


def test_empty_result_produces_empty_group_result():
    result = CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[], matches=[])
    gr = group_result(result)
    assert gr.total_keys == 0
    assert gr.groups == {}
    assert gr.ungrouped == []
