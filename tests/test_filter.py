"""Tests for envdiff.filter module."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.filter import filter_by_pattern, filter_by_prefix, filter_by_type


@pytest.fixture()
def sample_result() -> CompareResult:
    return CompareResult(
        missing_in_b=[
            KeyDiff(key="DB_HOST", value_a="localhost", value_b=None),
            KeyDiff(key="APP_NAME", value_a="myapp", value_b=None),
        ],
        missing_in_a=[
            KeyDiff(key="DB_PORT", value_a=None, value_b="5432"),
        ],
        mismatches=[
            KeyDiff(key="DB_USER", value_a="admin", value_b="root"),
            KeyDiff(key="SECRET_KEY", value_a="abc", value_b="xyz"),
        ],
    )


def test_filter_by_prefix_keeps_matching(sample_result):
    filtered = filter_by_prefix(sample_result, "DB_")
    keys_b = [d.key for d in filtered.missing_in_b]
    keys_a = [d.key for d in filtered.missing_in_a]
    keys_mm = [d.key for d in filtered.mismatches]

    assert keys_b == ["DB_HOST"]
    assert keys_a == ["DB_PORT"]
    assert keys_mm == ["DB_USER"]


def test_filter_by_prefix_case_insensitive(sample_result):
    filtered = filter_by_prefix(sample_result, "db_")
    assert len(filtered.missing_in_b) == 1
    assert filtered.missing_in_b[0].key == "DB_HOST"


def test_filter_by_prefix_no_match(sample_result):
    filtered = filter_by_prefix(sample_result, "REDIS_")
    assert filtered.missing_in_b == []
    assert filtered.missing_in_a == []
    assert filtered.mismatches == []


def test_filter_by_pattern_wildcard(sample_result):
    filtered = filter_by_pattern(sample_result, "DB_*")
    assert {d.key for d in filtered.missing_in_b} == {"DB_HOST"}
    assert {d.key for d in filtered.missing_in_a} == {"DB_PORT"}
    assert {d.key for d in filtered.mismatches} == {"DB_USER"}


def test_filter_by_pattern_question_mark(sample_result):
    # APP_NAME has 8 chars after APP_ — just verify pattern matching works
    filtered = filter_by_pattern(sample_result, "APP_????")
    assert len(filtered.missing_in_b) == 1
    assert filtered.missing_in_b[0].key == "APP_NAME"


def test_filter_by_pattern_no_match(sample_result):
    filtered = filter_by_pattern(sample_result, "NOPE_*")
    assert not filtered.missing_in_b
    assert not filtered.missing_in_a
    assert not filtered.mismatches


def test_filter_by_type_exclude_missing_b(sample_result):
    filtered = filter_by_type(sample_result, include_missing_b=False)
    assert filtered.missing_in_b == []
    assert len(filtered.missing_in_a) == 1
    assert len(filtered.mismatches) == 2


def test_filter_by_type_exclude_mismatches(sample_result):
    filtered = filter_by_type(sample_result, include_mismatches=False)
    assert filtered.mismatches == []
    assert len(filtered.missing_in_b) == 2


def test_filter_by_type_all_excluded(sample_result):
    filtered = filter_by_type(
        sample_result,
        include_missing_b=False,
        include_missing_a=False,
        include_mismatches=False,
    )
    assert not filtered.missing_in_b
    assert not filtered.missing_in_a
    assert not filtered.mismatches
