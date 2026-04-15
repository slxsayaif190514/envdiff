"""Tests for envdiff.scorer_formatter."""

from envdiff.scorer import CompatibilityScore
from envdiff.scorer_formatter import format_score


def _make(score, matching=2, total=4, mb=1, ma=0, mm=1):
    return CompatibilityScore(
        total_keys=total,
        matching_keys=matching,
        missing_in_b=mb,
        missing_in_a=ma,
        mismatched=mm,
        score=score,
    )


def test_output_contains_score_value():
    out = format_score(_make(75.0))
    assert "75.0" in out


def test_output_contains_grade():
    out = format_score(_make(95.0))
    assert "A" in out


def test_header_with_filenames():
    out = format_score(_make(80.0), file_a=".env.dev", file_b=".env.prod")
    assert ".env.dev" in out
    assert ".env.prod" in out


def test_header_without_filenames():
    out = format_score(_make(80.0))
    assert "Compatibility Score" in out
    # no 'vs' when files not provided
    assert "vs" not in out


def test_total_keys_shown():
    out = format_score(_make(60.0, total=10))
    assert "10" in out


def test_matching_keys_shown():
    out = format_score(_make(60.0, matching=5))
    assert "5" in out


def test_zero_mismatch_no_color_code_for_mismatch():
    s = CompatibilityScore(
        total_keys=2, matching_keys=2,
        missing_in_b=0, missing_in_a=0, mismatched=0, score=100.0
    )
    out = format_score(s)
    # value shown as plain '0' without ANSI yellow when zero mismatches
    assert "Mismatched" in out
    assert "0" in out


def test_nonzero_missing_present_in_output():
    s = _make(50.0, mb=3, ma=2)
    out = format_score(s)
    assert "3" in out
    assert "2" in out
