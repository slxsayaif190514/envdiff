"""Tests for envdiff.baseline and envdiff.baseline_formatter."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envdiff.baseline import BaselineDiff, BaselineResult, compare_against_baseline
from envdiff.baseline_formatter import format_baseline_result


def _make_snapshot(label: str, diffs: list) -> MagicMock:
    snap = MagicMock()
    snap.label = label
    snap.diffs = diffs
    return snap


_SNAP_DIFFS = [
    {"type": "match", "key": "HOST", "value_a": "localhost"},
    {"type": "mismatch", "key": "PORT", "value_a": "5432"},
    {"type": "missing_in_b", "key": "SECRET", "value_a": "abc"},
]


@pytest.fixture
def snapshot():
    return _make_snapshot("prod-2024", _SNAP_DIFFS)


def test_clean_when_identical(snapshot):
    current = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}
    result = compare_against_baseline(snapshot, current, env_file=".env")
    assert result.is_clean
    assert result.issue_count == 0


def test_detects_added_key(snapshot):
    current = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc", "NEW_KEY": "val"}
    result = compare_against_baseline(snapshot, current)
    assert len(result.added) == 1
    assert result.added[0].key == "NEW_KEY"
    assert result.added[0].kind == "added"


def test_detects_removed_key(snapshot):
    current = {"HOST": "localhost", "PORT": "5432"}
    result = compare_against_baseline(snapshot, current)
    assert any(d.key == "SECRET" for d in result.removed)


def test_detects_changed_value(snapshot):
    current = {"HOST": "remotehost", "PORT": "5432", "SECRET": "abc"}
    result = compare_against_baseline(snapshot, current)
    assert len(result.changed) == 1
    assert result.changed[0].key == "HOST"
    assert result.changed[0].baseline_value == "localhost"
    assert result.changed[0].current_value == "remotehost"


def test_issue_count_sums_all(snapshot):
    current = {"HOST": "changed", "EXTRA": "x"}  # removed PORT+SECRET, added EXTRA, changed HOST
    result = compare_against_baseline(snapshot, current)
    assert result.issue_count == len(result.added) + len(result.removed) + len(result.changed)


def test_snapshot_label_preserved(snapshot):
    result = compare_against_baseline(snapshot, {})
    assert result.snapshot_label == "prod-2024"


def test_env_file_stored(snapshot):
    result = compare_against_baseline(snapshot, {}, env_file="staging.env")
    assert result.env_file == "staging.env"


# --- formatter tests ---


def test_format_clean_result():
    result = BaselineResult(snapshot_label="snap", env_file=".env")
    out = format_baseline_result(result, color=False)
    assert "No changes" in out


def test_format_added_shown():
    result = BaselineResult(snapshot_label="snap", env_file=".env")
    result.added.append(BaselineDiff(key="FOO", baseline_value=None, current_value="bar", kind="added"))
    out = format_baseline_result(result, color=False)
    assert "FOO" in out
    assert "Added" in out


def test_format_removed_shown():
    result = BaselineResult(snapshot_label="snap", env_file=".env")
    result.removed.append(BaselineDiff(key="OLD", baseline_value="x", current_value=None, kind="removed"))
    out = format_baseline_result(result, color=False)
    assert "OLD" in out
    assert "Removed" in out


def test_format_changed_shown():
    result = BaselineResult(snapshot_label="snap", env_file=".env")
    result.changed.append(BaselineDiff(key="PORT", baseline_value="5432", current_value="3306", kind="changed"))
    out = format_baseline_result(result, color=False)
    assert "PORT" in out
    assert "Changed" in out
    assert "5432" in out
    assert "3306" in out


def test_format_header_contains_label():
    result = BaselineResult(snapshot_label="my-snap", env_file="prod.env")
    out = format_baseline_result(result, color=False)
    assert "my-snap" in out
    assert "prod.env" in out
