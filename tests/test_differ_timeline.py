"""Tests for differ_timeline and timeline_formatter."""

from __future__ import annotations

import pytest

from envdiff.differ_timeline import (
    TimelineEntry,
    KeyTimeline,
    TimelineResult,
    build_timeline,
)
from envdiff.timeline_formatter import format_timeline
from envdiff.snapshotter import Snapshot


def _snap(label: str, env_a: dict, env_b: dict) -> Snapshot:
    return Snapshot(label=label, env_a=env_a, env_b=env_b, diffs=[])


# ---------------------------------------------------------------------------
# KeyTimeline helpers
# ---------------------------------------------------------------------------

def test_stable_when_all_same():
    tl = KeyTimeline(key="FOO", entries=[
        TimelineEntry("v1", "bar"),
        TimelineEntry("v2", "bar"),
    ])
    assert tl.is_stable is True
    assert tl.change_count == 0


def test_unstable_when_value_changes():
    tl = KeyTimeline(key="FOO", entries=[
        TimelineEntry("v1", "bar"),
        TimelineEntry("v2", "baz"),
    ])
    assert tl.is_stable is False
    assert tl.change_count == 1


def test_absent_to_present_counts_as_change():
    tl = KeyTimeline(key="FOO", entries=[
        TimelineEntry("v1", None),
        TimelineEntry("v2", "hello"),
    ])
    assert tl.change_count == 1


def test_latest_value_returns_last_entry():
    tl = KeyTimeline(key="FOO", entries=[
        TimelineEntry("v1", "a"),
        TimelineEntry("v2", "b"),
    ])
    assert tl.latest_value == "b"


def test_latest_value_empty_entries():
    tl = KeyTimeline(key="FOO", entries=[])
    assert tl.latest_value is None


# ---------------------------------------------------------------------------
# build_timeline
# ---------------------------------------------------------------------------

def test_build_timeline_single_snapshot():
    snap = _snap("v1", {"A": "1"}, {"A": "1", "B": "2"})
    result = build_timeline([snap])
    keys = [t.key for t in result.timelines]
    assert "A" in keys
    assert "B" in keys


def test_build_timeline_value_changes_across_snapshots():
    s1 = _snap("v1", {"DB_URL": "old"}, {})
    s2 = _snap("v2", {"DB_URL": "new"}, {})
    result = build_timeline([s1, s2])
    db = next(t for t in result.timelines if t.key == "DB_URL")
    assert db.change_count == 1
    assert db.is_stable is False


def test_build_timeline_stable_key():
    s1 = _snap("v1", {"PORT": "8080"}, {})
    s2 = _snap("v2", {"PORT": "8080"}, {})
    result = build_timeline([s1, s2])
    port = next(t for t in result.timelines if t.key == "PORT")
    assert port.is_stable is True


def test_timeline_result_stable_unstable_split():
    s1 = _snap("v1", {"A": "1", "B": "x"}, {})
    s2 = _snap("v2", {"A": "1", "B": "y"}, {})
    result = build_timeline([s1, s2])
    assert len(result.stable_keys) == 1
    assert len(result.unstable_keys) == 1


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_timeline_contains_key_name():
    s1 = _snap("v1", {"SECRET": "abc"}, {})
    result = build_timeline([s1])
    output = format_timeline(result, color=False)
    assert "SECRET" in output


def test_format_timeline_shows_stable_label():
    s1 = _snap("v1", {"X": "1"}, {})
    s2 = _snap("v2", {"X": "1"}, {})
    result = build_timeline([s1, s2])
    output = format_timeline(result, color=False)
    assert "stable" in output


def test_format_timeline_shows_change_count():
    s1 = _snap("v1", {"X": "1"}, {})
    s2 = _snap("v2", {"X": "2"}, {})
    result = build_timeline([s1, s2])
    output = format_timeline(result, color=False)
    assert "1 change" in output


def test_format_timeline_empty():
    result = TimelineResult(timelines=[])
    output = format_timeline(result, color=False)
    assert "(no keys)" in output
