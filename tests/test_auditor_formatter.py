"""Tests for envdiff.auditor_formatter."""
from __future__ import annotations

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.auditor import audit_diff
from envdiff.auditor_formatter import format_audit_report


def _diff(key, va=None, vb=None):
    return KeyDiff(key=key, value_a=va, value_b=vb)


@pytest.fixture()
def clean_report():
    result = CompareResult([], [], [], [_diff("KEY", va="v", vb="v")])
    return audit_diff(result, file_a="a.env", file_b="b.env")


@pytest.fixture()
def dirty_report():
    result = CompareResult(
        missing_in_b=[_diff("GONE", va="old")],
        missing_in_a=[_diff("NEW", vb="fresh")],
        mismatches=[_diff("MOD", va="1", vb="2")],
        matches=[],
    )
    return audit_diff(result, file_a="a.env", file_b="b.env")


def test_clean_shows_no_changes(clean_report):
    out = format_audit_report(clean_report, plain=True)
    assert "No changes detected" in out


def test_header_contains_filenames(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "a.env" in out
    assert "b.env" in out


def test_added_key_shown(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "NEW" in out
    assert "fresh" in out


def test_removed_key_shown(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "GONE" in out
    assert "old" in out


def test_modified_key_shown(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "MOD" in out


def test_total_changes_shown(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "3" in out


def test_ansi_codes_present_by_default(dirty_report):
    out = format_audit_report(dirty_report, plain=False)
    assert "\033[" in out


def test_plain_mode_no_ansi(dirty_report):
    out = format_audit_report(dirty_report, plain=True)
    assert "\033[" not in out
