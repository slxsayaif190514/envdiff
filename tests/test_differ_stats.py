"""Tests for envdiff.differ_stats."""
import pytest
from envdiff.comparator import CompareResult, KeyDiff
from envdiff.differ_stats import DiffStats, compute_stats


def _diff(key, val_a=None, val_b=None):
    return KeyDiff(key=key, value_a=val_a, value_b=val_b)


@pytest.fixture
def empty_result():
    return CompareResult([], [], [], [])


@pytest.fixture
def mixed_result():
    return CompareResult(
        missing_in_b=[_diff("ONLY_A", val_a="1")],
        missing_in_a=[_diff("ONLY_B", val_b="2")],
        mismatches=[_diff("CLASH", val_a="x", val_b="y")],
        matching=[_diff("SHARED", val_a="ok", val_b="ok")],
    )


def test_empty_result_all_zeros(empty_result):
    stats = compute_stats(empty_result)
    assert stats.total_keys == 0
    assert stats.matched == 0
    assert stats.missing_in_a == 0
    assert stats.missing_in_b == 0
    assert stats.mismatched == 0


def test_empty_result_match_rate_100(empty_result):
    stats = compute_stats(empty_result)
    assert stats.match_rate == 100.0


def test_mixed_result_total(mixed_result):
    stats = compute_stats(mixed_result)
    assert stats.total_keys == 4


def test_mixed_result_counts(mixed_result):
    stats = compute_stats(mixed_result)
    assert stats.matched == 1
    assert stats.missing_in_a == 1
    assert stats.missing_in_b == 1
    assert stats.mismatched == 1


def test_mixed_result_has_issues(mixed_result):
    stats = compute_stats(mixed_result)
    assert stats.has_issues is True
    assert stats.issue_count == 3


def test_perfect_result_no_issues():
    result = CompareResult(
        missing_in_b=[],
        missing_in_a=[],
        mismatches=[],
        matching=[_diff("A", "1", "1"), _diff("B", "2", "2")],
    )
    stats = compute_stats(result)
    assert stats.has_issues is False
    assert stats.match_rate == 100.0


def test_match_rate_partial():
    result = CompareResult(
        missing_in_b=[_diff("X", val_a="1")],
        missing_in_a=[],
        mismatches=[],
        matching=[_diff("Y", "2", "2"), _diff("Z", "3", "3"), _diff("W", "4", "4")],
    )
    stats = compute_stats(result)
    assert stats.match_rate == 75.0


def test_files_stored():
    result = CompareResult([], [], [], [])
    stats = compute_stats(result, file_a=".env.dev", file_b=".env.prod")
    assert stats.files == [".env.dev", ".env.prod"]


def test_files_empty_strings_excluded():
    result = CompareResult([], [], [], [])
    stats = compute_stats(result, file_a=".env", file_b="")
    assert stats.files == [".env"]
