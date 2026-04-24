"""Tests for envdiff.digester_formatter."""

from __future__ import annotations

from envdiff.digester import digest_env, compare_digests
from envdiff.digester_formatter import format_digest_result, format_digest_diff


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "remotehost", "DB_PORT": "5432", "NEW_KEY": "xyz"}


def _strip(s: str) -> str:
    """Remove ANSI escape codes for plain-text assertions."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_format_digest_result_contains_filename():
    result = digest_env("dev.env", ENV_A)
    out = _strip(format_digest_result(result))
    assert "dev.env" in out


def test_format_digest_result_shows_key_count():
    result = digest_env("dev.env", ENV_A)
    out = _strip(format_digest_result(result))
    assert "3" in out


def test_format_digest_result_lists_keys():
    result = digest_env("dev.env", ENV_A)
    out = _strip(format_digest_result(result))
    assert "DB_HOST" in out
    assert "SECRET" in out


def test_format_digest_result_shows_partial_hash():
    result = digest_env("dev.env", ENV_A)
    out = _strip(format_digest_result(result))
    # at least one truncated hash stub should appear
    assert "..." in out


def test_format_digest_diff_no_diffs_shows_match():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_A)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "match" in out.lower()


def test_format_digest_diff_header_contains_both_files():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_B)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "a.env" in out
    assert "b.env" in out


def test_format_digest_diff_changed_key_shown():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_B)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "DB_HOST" in out


def test_format_digest_diff_only_in_a_shown():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_B)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "SECRET" in out


def test_format_digest_diff_only_in_b_shown():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_B)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "NEW_KEY" in out


def test_format_digest_diff_difference_count_shown():
    a = digest_env("a.env", ENV_A)
    b = digest_env("b.env", ENV_B)
    diffs = compare_digests(a, b)
    out = _strip(format_digest_diff(a, b, diffs))
    assert "difference" in out.lower()
