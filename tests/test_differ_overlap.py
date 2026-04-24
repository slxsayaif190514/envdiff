"""Tests for differ_overlap and overlap_formatter."""
from __future__ import annotations

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.differ_overlap import OverlapResult, compute_overlap
from envdiff.overlap_formatter import format_overlap_result


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_result(
    missing_in_b=(),
    missing_in_a=(),
    mismatches=(),
    matches=(),
) -> CompareResult:
    return CompareResult(
        missing_in_b=[KeyDiff(k, "v", None) for k in missing_in_b],
        missing_in_a=[KeyDiff(k, None, "v") for k in missing_in_a],
        mismatches=[KeyDiff(k, "old", "new") for k in mismatches],
        matches=[KeyDiff(k, "v", "v") for k in matches],
    )


# ---------------------------------------------------------------------------
# compute_overlap
# ---------------------------------------------------------------------------

def test_identical_envs_full_overlap():
    env = {"A": "1", "B": "2"}
    cr = _make_result(matches=["A", "B"])
    res = compute_overlap(cr, env, env, "x", "y")
    assert res.shared_keys == {"A", "B"}
    assert res.only_in_a == set()
    assert res.only_in_b == set()
    assert res.overlap_ratio == 1.0
    assert res.value_match_ratio == 1.0


def test_disjoint_envs_zero_overlap():
    env_a = {"A": "1"}
    env_b = {"B": "2"}
    cr = _make_result(missing_in_b=["A"], missing_in_a=["B"])
    res = compute_overlap(cr, env_a, env_b)
    assert res.shared_keys == set()
    assert res.only_in_a == {"A"}
    assert res.only_in_b == {"B"}
    assert res.overlap_ratio == 0.0
    assert res.total_unique_keys == 2


def test_partial_overlap_with_mismatch():
    env_a = {"A": "1", "B": "old", "C": "3"}
    env_b = {"B": "new", "C": "3", "D": "4"}
    cr = _make_result(
        missing_in_b=["A"],
        missing_in_a=["D"],
        mismatches=["B"],
        matches=["C"],
    )
    res = compute_overlap(cr, env_a, env_b, "dev", "prod")
    assert res.shared_keys == {"B", "C"}
    assert res.only_in_a == {"A"}
    assert res.only_in_b == {"D"}
    assert res.value_matches == {"C"}
    assert res.value_mismatches == {"B"}
    assert res.value_match_ratio == 0.5


def test_empty_envs_ratios_are_one():
    cr = _make_result()
    res = compute_overlap(cr, {}, {})
    assert res.total_unique_keys == 0
    assert res.overlap_ratio == 1.0
    assert res.value_match_ratio == 1.0


def test_file_names_stored():
    cr = _make_result()
    res = compute_overlap(cr, {}, {}, "alpha", "beta")
    assert res.file_a == "alpha"
    assert res.file_b == "beta"


# ---------------------------------------------------------------------------
# format_overlap_result
# ---------------------------------------------------------------------------

def _strip(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]+m", "", s)


def test_format_contains_filenames():
    cr = _make_result()
    res = compute_overlap(cr, {}, {}, "dev.env", "prod.env")
    out = _strip(format_overlap_result(res))
    assert "dev.env" in out
    assert "prod.env" in out


def test_format_shows_shared_count():
    env = {"X": "1", "Y": "2"}
    cr = _make_result(matches=["X", "Y"])
    res = compute_overlap(cr, env, env)
    out = _strip(format_overlap_result(res))
    assert "2" in out


def test_format_lists_only_in_a_keys():
    env_a = {"ONLY_A": "1"}
    env_b: dict = {}
    cr = _make_result(missing_in_b=["ONLY_A"])
    res = compute_overlap(cr, env_a, env_b, "a", "b")
    out = _strip(format_overlap_result(res))
    assert "ONLY_A" in out


def test_format_lists_only_in_b_keys():
    env_a: dict = {}
    env_b = {"ONLY_B": "1"}
    cr = _make_result(missing_in_a=["ONLY_B"])
    res = compute_overlap(cr, env_a, env_b, "a", "b")
    out = _strip(format_overlap_result(res))
    assert "ONLY_B" in out


def test_format_no_only_section_when_empty():
    env = {"K": "v"}
    cr = _make_result(matches=["K"])
    res = compute_overlap(cr, env, env)
    out = _strip(format_overlap_result(res))
    assert "Keys only in" not in out
