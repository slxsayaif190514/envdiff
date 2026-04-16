"""Tests for envdiff.pinner_formatter."""
from envdiff.pinner import PinEntry, PinResult
from envdiff.pinner_formatter import format_pin_result


def _make(entries, filename="a.env"):
    r = PinResult(filename=filename)
    r.entries = entries
    return r


def test_clean_result_shows_pass():
    result = _make([PinEntry("K", "v", "v")])
    out = format_pin_result(result, color=False)
    assert "No drift" in out


def test_clean_result_shows_filename():
    result = _make([], filename="prod.env")
    out = format_pin_result(result, color=False)
    assert "prod.env" in out


def test_drifted_key_shown():
    result = _make([PinEntry("FOO", "old", "new")])
    out = format_pin_result(result, color=False)
    assert "FOO" in out


def test_removed_key_shown():
    result = _make([PinEntry("BAR", "x", None)])
    out = format_pin_result(result, color=False)
    assert "BAR" in out
    assert "removed" in out


def test_drift_count_shown():
    result = _make([PinEntry("A", "1", "2"), PinEntry("B", "x", "x")])
    out = format_pin_result(result, color=False)
    assert "1 drifted" in out


def test_non_drifted_key_not_highlighted():
    result = _make([PinEntry("STABLE", "v", "v"), PinEntry("CHANGED", "a", "b")])
    out = format_pin_result(result, color=False)
    lines = out.splitlines()
    drifted_lines = [l for l in lines if "STABLE" in l]
    assert not drifted_lines
