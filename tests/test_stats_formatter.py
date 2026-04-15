"""Tests for envdiff.stats_formatter."""
import pytest
from envdiff.differ_stats import DiffStats
from envdiff.stats_formatter import format_stats


def _make(matched=0, missing_a=0, missing_b=0, mismatched=0, files=None):
    total = matched + missing_a + missing_b + mismatched
    return DiffStats(
        total_keys=total,
        matched=matched,
        missing_in_a=missing_a,
        missing_in_b=missing_b,
        mismatched=mismatched,
        files=files or [],
    )


def test_header_present():
    out = format_stats(_make(), color=False)
    assert "Diff Statistics" in out


def test_files_in_header():
    stats = _make(files=[".env.dev", ".env.prod"])
    out = format_stats(stats, color=False)
    assert ".env.dev" in out
    assert ".env.prod" in out


def test_total_keys_shown():
    stats = _make(matched=2, missing_a=1)
    out = format_stats(stats, color=False)
    assert "3" in out


def test_all_keys_match_message():
    stats = _make(matched=3)
    out = format_stats(stats, color=False)
    assert "All keys match" in out


def test_issues_found_message():
    stats = _make(matched=1, mismatched=2)
    out = format_stats(stats, color=False)
    assert "issue" in out


def test_match_rate_shown():
    stats = _make(matched=3, missing_b=1)
    out = format_stats(stats, color=False)
    assert "75.0%" in out


def test_color_output_contains_ansi():
    stats = _make(matched=1, mismatched=1)
    out = format_stats(stats, color=True)
    assert "\033[" in out


def test_no_color_no_ansi():
    stats = _make(matched=1)
    out = format_stats(stats, color=False)
    assert "\033[" not in out


def test_missing_in_a_count_shown():
    stats = _make(missing_a=3)
    out = format_stats(stats, color=False)
    assert "Missing in A" in out


def test_missing_in_b_count_shown():
    stats = _make(missing_b=2)
    out = format_stats(stats, color=False)
    assert "Missing in B" in out
