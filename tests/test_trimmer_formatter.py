import pytest
from envdiff.trimmer import trim_env
from envdiff.trimmer_formatter import format_trim_result


def _make(env, ref, filename="test.env"):
    return trim_env(env, ref, filename=filename)


def test_clean_result_shows_no_unused():
    result = _make({"A": "1"}, {"A": "1"})
    out = format_trim_result(result, color=False)
    assert "No unused keys found" in out


def test_filename_in_header():
    result = _make({}, {}, filename="prod.env")
    out = format_trim_result(result, color=False)
    assert "prod.env" in out


def test_removed_key_shown():
    result = _make({"GHOST": "val", "KEEP": "x"}, {"KEEP": "x"})
    out = format_trim_result(result, color=False)
    assert "GHOST" in out


def test_removed_count_shown():
    result = _make({"X": "1", "Y": "2"}, {})
    out = format_trim_result(result, color=False)
    assert "2" in out


def test_kept_count_shown():
    result = _make({"A": "1", "B": "2"}, {"A": "1"})
    out = format_trim_result(result, color=False)
    assert "Kept 1" in out


def test_no_filename_fallback():
    result = trim_env({}, {})
    out = format_trim_result(result, color=False)
    assert "Trim result" in out
