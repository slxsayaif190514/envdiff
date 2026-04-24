"""Tests for differ_drift and drift_formatter."""

import pytest

from envdiff.differ_drift import detect_drift, DriftEntry, DriftResult
from envdiff.drift_formatter import format_drift_result


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_no_drift_when_identical():
    env = {"A": "1", "B": "2"}
    result = detect_drift(env, env.copy())
    assert result.is_clean
    assert result.drift_count == 0


def test_added_key_detected():
    source = {"A": "1"}
    target = {"A": "1", "B": "2"}
    result = detect_drift(source, target)
    added = result.by_type("added")
    assert len(added) == 1
    assert added[0].key == "B"
    assert added[0].new_value == "2"
    assert added[0].old_value is None


def test_removed_key_detected():
    source = {"A": "1", "B": "2"}
    target = {"A": "1"}
    result = detect_drift(source, target)
    removed = result.by_type("removed")
    assert len(removed) == 1
    assert removed[0].key == "B"
    assert removed[0].old_value == "2"
    assert removed[0].new_value is None


def test_changed_value_detected():
    source = {"DB_URL": "postgres://old"}
    target = {"DB_URL": "postgres://new"}
    result = detect_drift(source, target)
    changed = result.by_type("changed")
    assert len(changed) == 1
    assert changed[0].key == "DB_URL"
    assert changed[0].old_value == "postgres://old"
    assert changed[0].new_value == "postgres://new"


def test_mixed_drift():
    source = {"A": "1", "B": "old", "C": "keep"}
    target = {"B": "new", "C": "keep", "D": "added"}
    result = detect_drift(source, target)
    assert not result.is_clean
    assert len(result.by_type("removed")) == 1
    assert len(result.by_type("changed")) == 1
    assert len(result.by_type("added")) == 1
    assert result.drift_count == 3


def test_labels_stored():
    result = detect_drift({}, {}, source_label="v1", target_label="v2")
    assert result.source_label == "v1"
    assert result.target_label == "v2"


def test_entries_sorted_by_key():
    source = {"Z": "1", "A": "old"}
    target = {"Z": "2", "A": "new"}
    result = detect_drift(source, target)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_repr_drift_entry():
    e = DriftEntry(key="X", old_value="a", new_value="b", drift_type="changed")
    assert "X" in repr(e)
    assert "changed" in repr(e)


def test_repr_drift_result():
    r = DriftResult(source_label="a", target_label="b")
    assert "a" in repr(r)
    assert "b" in repr(r)


# ---------------------------------------------------------------------------
# format_drift_result
# ---------------------------------------------------------------------------

def _strip(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_format_clean_result_shows_no_drift():
    result = detect_drift({"A": "1"}, {"A": "1"}, source_label="old", target_label="new")
    out = _strip(format_drift_result(result))
    assert "No drift" in out


def test_format_shows_added_key():
    result = detect_drift({}, {"NEW_KEY": "val"}, source_label="s", target_label="t")
    out = _strip(format_drift_result(result))
    assert "NEW_KEY" in out
    assert "+" in out


def test_format_shows_removed_key():
    result = detect_drift({"OLD_KEY": "v"}, {}, source_label="s", target_label="t")
    out = _strip(format_drift_result(result))
    assert "OLD_KEY" in out
    assert "-" in out


def test_format_shows_changed_key():
    result = detect_drift({"K": "a"}, {"K": "b"}, source_label="s", target_label="t")
    out = _strip(format_drift_result(result))
    assert "K" in out
    assert "~" in out


def test_format_summary_counts():
    source = {"A": "1", "B": "old"}
    target = {"B": "new", "C": "fresh"}
    result = detect_drift(source, target)
    out = _strip(format_drift_result(result))
    assert "1 added" in out
    assert "1 removed" in out
    assert "1 changed" in out


def test_format_header_contains_labels():
    result = detect_drift({}, {}, source_label="env.v1", target_label="env.v2")
    out = _strip(format_drift_result(result))
    assert "env.v1" in out
    assert "env.v2" in out
