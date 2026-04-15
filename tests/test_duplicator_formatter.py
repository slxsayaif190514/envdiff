"""Tests for envdiff.duplicator_formatter."""
from __future__ import annotations

import pytest

from envdiff.duplicator import DuplicateResult, DuplicateEntry
from envdiff.duplicator_formatter import format_duplicate_result


def _make(duplicates=None) -> DuplicateResult:
    return DuplicateResult(
        filename=".env.test",
        duplicates=duplicates or [],
    )


def test_clean_result_shows_pass():
    out = format_duplicate_result(_make(), color=False)
    assert "No duplicate keys found" in out


def test_clean_result_shows_filename():
    out = format_duplicate_result(_make(), color=False)
    assert ".env.test" in out


def test_duplicate_count_shown():
    dup = DuplicateEntry(key="FOO", lines=[1, 5], values=["a", "b"])
    out = format_duplicate_result(_make([dup]), color=False)
    assert "1" in out
    assert "duplicate" in out.lower()


def test_key_name_shown():
    dup = DuplicateEntry(key="MY_KEY", lines=[2, 8], values=["x", "x"])
    out = format_duplicate_result(_make([dup]), color=False)
    assert "MY_KEY" in out


def test_conflict_tag_shown_for_differing_values():
    dup = DuplicateEntry(key="TOKEN", lines=[1, 3], values=["old", "new"])
    out = format_duplicate_result(_make([dup]), color=False)
    assert "conflict" in out.lower()


def test_duplicate_tag_shown_for_same_values():
    dup = DuplicateEntry(key="PORT", lines=[1, 4], values=["8080", "8080"])
    out = format_duplicate_result(_make([dup]), color=False)
    assert "duplicate" in out.lower()
    assert "conflict" not in out.lower()


def test_line_numbers_shown():
    dup = DuplicateEntry(key="DB", lines=[3, 7], values=["a", "b"])
    out = format_duplicate_result(_make([dup]), color=False)
    assert "3" in out
    assert "7" in out


def test_color_output_contains_ansi():
    dup = DuplicateEntry(key="X", lines=[1, 2], values=["p", "q"])
    out = format_duplicate_result(_make([dup]), color=True)
    assert "\033[" in out
