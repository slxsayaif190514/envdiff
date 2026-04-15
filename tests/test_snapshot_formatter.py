"""Tests for envdiff.snapshot_formatter."""
import pytest

from envdiff.comparator import KeyDiff
from envdiff.snapshotter import Snapshot
from envdiff.snapshot_formatter import format_snapshot


@pytest.fixture()
def snap_with_diffs() -> Snapshot:
    return Snapshot(
        label="release-1.2",
        created_at="2024-06-01T12:00:00+00:00",
        file_a=".env.dev",
        file_b=".env.prod",
        diffs=[
            KeyDiff("DB_HOST", "missing_in_b", "localhost", None),
            KeyDiff("SECRET", "missing_in_a", None, "s3cr3t"),
            KeyDiff("LOG_LEVEL", "mismatch", "debug", "error"),
        ],
    )


@pytest.fixture()
def snap_empty() -> Snapshot:
    return Snapshot(
        label="clean",
        created_at="2024-06-01T12:00:00+00:00",
        file_a="a",
        file_b="b",
        diffs=[],
    )


def test_label_in_output(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert "release-1.2" in out


def test_file_names_shown(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert ".env.dev" in out
    assert ".env.prod" in out


def test_diff_count_shown(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert "3 difference" in out


def test_missing_in_b_shown(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert "DB_HOST" in out
    assert "missing_in_b" in out


def test_missing_in_a_shown(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert "SECRET" in out
    assert "missing_in_a" in out


def test_mismatch_shown(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=False)
    assert "LOG_LEVEL" in out
    assert "mismatch" in out


def test_no_diffs_message(snap_empty):
    out = format_snapshot(snap_empty, color=False)
    assert "No differences" in out


def test_color_output_contains_ansi(snap_with_diffs):
    out = format_snapshot(snap_with_diffs, color=True)
    assert "\033[" in out
