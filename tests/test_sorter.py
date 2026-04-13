"""Tests for envdiff.sorter."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.sorter import SortKey, sort_result


def _diff(key, diff_type, val_a=None, val_b=None):
    return KeyDiff(key=key, diff_type=diff_type, value_a=val_a, value_b=val_b)


@pytest.fixture()
def mixed_result():
    return CompareResult(
        missing_in_b=[_diff("ZEBRA", "missing_in_b", val_a="1"), _diff("ALPHA", "missing_in_b", val_a="2")],
        missing_in_a=[_diff("MANGO", "missing_in_a", val_b="x")],
        mismatches=[_diff("PORT", "mismatch", val_a="80", val_b="8080"), _diff("HOST", "mismatch", val_a="a", val_b="b")],
    )


def test_sort_by_key_alphabetical(mixed_result):
    result = sort_result(mixed_result, by=SortKey.KEY)
    all_keys = (
        [d.key for d in result.missing_in_b]
        + [d.key for d in result.missing_in_a]
        + [d.key for d in result.mismatches]
    )
    assert all_keys == sorted(all_keys, key=str.lower)


def test_sort_by_key_reverse(mixed_result):
    result = sort_result(mixed_result, by=SortKey.KEY, reverse=True)
    all_keys = (
        [d.key for d in result.missing_in_b]
        + [d.key for d in result.missing_in_a]
        + [d.key for d in result.mismatches]
    )
    assert all_keys == sorted(all_keys, key=str.lower, reverse=True)


def test_sort_by_type_preserves_categories(mixed_result):
    result = sort_result(mixed_result, by=SortKey.TYPE)
    # within each bucket keys should be sorted
    assert [d.key for d in result.missing_in_b] == ["ALPHA", "ZEBRA"]
    assert [d.key for d in result.mismatches] == ["HOST", "PORT"]


def test_sort_preserves_all_diffs(mixed_result):
    result = sort_result(mixed_result, by=SortKey.KEY)
    original_count = (
        len(mixed_result.missing_in_b)
        + len(mixed_result.missing_in_a)
        + len(mixed_result.mismatches)
    )
    new_count = (
        len(result.missing_in_b)
        + len(result.missing_in_a)
        + len(result.mismatches)
    )
    assert original_count == new_count


def test_sort_empty_result():
    empty = CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[])
    result = sort_result(empty, by=SortKey.KEY)
    assert result.missing_in_b == []
    assert result.missing_in_a == []
    assert result.mismatches == []


def test_sort_by_status(mixed_result):
    result = sort_result(mixed_result, by=SortKey.STATUS)
    # mismatches have both values so they come first
    mismatch_keys = {d.key for d in result.mismatches}
    assert "PORT" in mismatch_keys
    assert "HOST" in mismatch_keys
