"""Tests for differ_age and age_formatter."""

from datetime import datetime, timedelta

import pytest

from envdiff.differ_age import AgeEntry, AgeResult, build_age_result
from envdiff.age_formatter import format_age_result


BASE = datetime(2023, 1, 1)
OLD = BASE
NEW = BASE + timedelta(days=120)
MID = BASE + timedelta(days=30)


def _snap(keys):
    return {k: "val" for k in keys}


# --- AgeEntry ---

def test_age_entry_age_days_none_when_missing_dates():
    e = AgeEntry(key="X", last_seen=None, first_seen=None, snapshot_count=1)
    assert e.age_days is None


def test_age_entry_age_days_computed():
    e = AgeEntry(key="X", first_seen=OLD, last_seen=NEW, snapshot_count=5)
    assert abs(e.age_days - 120.0) < 0.01


def test_age_entry_not_stale_single_snapshot():
    e = AgeEntry(key="X", first_seen=OLD, last_seen=NEW, snapshot_count=1)
    assert not e.is_stale


def test_age_entry_stale_when_old_and_multiple_snapshots():
    e = AgeEntry(key="X", first_seen=OLD, last_seen=NEW, snapshot_count=3)
    assert e.is_stale


def test_age_entry_not_stale_recent():
    e = AgeEntry(key="X", first_seen=MID, last_seen=NEW, snapshot_count=3)
    assert not e.is_stale  # 90 days exactly is not stale (> 90 required)


# --- build_age_result ---

def test_build_age_result_empty():
    result = build_age_result("test.env", [], [])
    assert result.key_count == 0
    assert result.is_clean


def test_build_age_result_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        build_age_result("test.env", [_snap(["A"])], [])


def test_build_age_result_single_snapshot():
    result = build_age_result("test.env", [_snap(["A", "B"])], [BASE])
    assert result.key_count == 2
    assert result.entries[0].snapshot_count == 1


def test_build_age_result_key_seen_in_all_snapshots():
    snaps = [_snap(["A"]), _snap(["A"]), _snap(["A"])]
    ts = [OLD, MID, NEW]
    result = build_age_result("test.env", snaps, ts)
    entry = result.entries[0]
    assert entry.snapshot_count == 3
    assert entry.first_seen == OLD
    assert entry.last_seen == NEW


def test_build_age_result_key_only_in_first_snapshot():
    snaps = [_snap(["A", "B"]), _snap(["B"]), _snap(["B"])]
    ts = [OLD, MID, NEW]
    result = build_age_result("test.env", snaps, ts)
    a = next(e for e in result.entries if e.key == "A")
    assert a.snapshot_count == 1
    assert not a.is_stale


def test_stale_keys_identified():
    snaps = [_snap(["A"]), _snap(["A"]), _snap(["A"])]
    ts = [OLD, MID, NEW]
    result = build_age_result("test.env", snaps, ts)
    assert result.stale_count == 1
    assert result.stale_keys[0].key == "A"


# --- format_age_result ---

def test_format_no_color_removes_escape_codes():
    snaps = [_snap(["X"]), _snap(["X"])]
    ts = [OLD, NEW]
    result = build_age_result("test.env", snaps, ts)
    out = format_age_result(result, no_color=True)
    assert "\033[" not in out


def test_format_shows_filename():
    result = AgeResult(filename="prod.env", entries=[])
    out = format_age_result(result, no_color=True)
    assert "prod.env" in out


def test_format_clean_message_when_no_stale():
    result = AgeResult(filename="a.env", entries=[
        AgeEntry(key="K", first_seen=MID, last_seen=NEW, snapshot_count=1)
    ])
    out = format_age_result(result, no_color=True)
    assert "No stale keys" in out


def test_format_stale_warning_shown():
    result = AgeResult(filename="a.env", entries=[
        AgeEntry(key="OLD_KEY", first_seen=OLD, last_seen=NEW, snapshot_count=5)
    ])
    out = format_age_result(result, no_color=True)
    assert "stale" in out.lower()
    assert "OLD_KEY" in out
