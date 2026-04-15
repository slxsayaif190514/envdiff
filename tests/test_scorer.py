"""Tests for envdiff.scorer."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.scorer import CompatibilityScore, score_result


def _diff(key, val_a=None, val_b=None):
    return KeyDiff(key=key, value_a=val_a, value_b=val_b)


@pytest.fixture()
def empty_result():
    return CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[], matches=[])


@pytest.fixture()
def perfect_result():
    return CompareResult(
        missing_in_b=[],
        missing_in_a=[],
        mismatches=[],
        matches=[_diff("A", "1", "1"), _diff("B", "2", "2")],
    )


@pytest.fixture()
def mixed_result():
    return CompareResult(
        missing_in_b=[_diff("ONLY_A", "x", None)],
        missing_in_a=[_diff("ONLY_B", None, "y")],
        mismatches=[_diff("DIFF", "old", "new")],
        matches=[_diff("SAME", "v", "v")],
    )


def test_empty_result_scores_100(empty_result):
    s = score_result(empty_result)
    assert s.score == 100.0
    assert s.total_keys == 0


def test_perfect_result_scores_100(perfect_result):
    s = score_result(perfect_result)
    assert s.score == 100.0
    assert s.matching_keys == 2
    assert s.grade() == "A"


def test_mixed_result_partial_score(mixed_result):
    s = score_result(mixed_result)
    # 4 total keys, penalty = 1 + 1 + 0.5 = 2.5 → score = (4-2.5)/4 * 100 = 37.5
    assert s.total_keys == 4
    assert s.score == pytest.approx(37.5)
    assert s.grade() == "F"


def test_only_mismatches_half_penalty():
    result = CompareResult(
        missing_in_b=[],
        missing_in_a=[],
        mismatches=[_diff("K", "a", "b")],
        matches=[_diff("M", "v", "v")],
    )
    s = score_result(result)
    # 2 total, penalty 0.5 → score = 1.5/2*100 = 75
    assert s.score == pytest.approx(75.0)
    assert s.grade() == "B"


def test_all_missing_scores_zero():
    result = CompareResult(
        missing_in_b=[_diff("A"), _diff("B")],
        missing_in_a=[],
        mismatches=[],
        matches=[],
    )
    s = score_result(result)
    assert s.score == 0.0
    assert s.grade() == "F"


def test_score_fields_populated(mixed_result):
    s = score_result(mixed_result)
    assert s.missing_in_b == 1
    assert s.missing_in_a == 1
    assert s.mismatched == 1
    assert s.matching_keys == 1


def test_grade_boundaries():
    def _score(v):
        return CompatibilityScore(
            total_keys=1, matching_keys=0,
            missing_in_b=0, missing_in_a=0, mismatched=0, score=v
        )
    assert _score(95.0).grade() == "A"
    assert _score(80.0).grade() == "B"
    assert _score(60.0).grade() == "C"
    assert _score(40.0).grade() == "D"
    assert _score(39.9).grade() == "F"
