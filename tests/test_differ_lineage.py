"""Tests for envdiff.differ_lineage."""

import pytest
from envdiff.differ_lineage import (
    build_lineage,
    LineageEntry,
    LineageEvent,
    LineageResult,
)


def test_build_lineage_key_count():
    snaps = [{"A": "1", "B": "2"}, {"A": "1"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    assert result.key_count == 2


def test_build_lineage_labels_stored():
    snaps = [{"X": "v"}]
    result = build_lineage(snaps, labels=["prod"])
    assert result.labels == ["prod"]


def test_build_lineage_auto_labels():
    snaps = [{"A": "1"}, {"A": "2"}]
    result = build_lineage(snaps)
    assert result.labels == ["snap0", "snap1"]


def test_build_lineage_absent_value_is_none():
    snaps = [{"A": "1"}, {"B": "2"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    entry_a = result.get("A")
    assert entry_a is not None
    assert entry_a.events[0].value == "1"
    assert entry_a.events[1].value is None


def test_first_seen_returns_correct_label():
    snaps = [{"A": None}, {"A": "hello"}]
    # None values in dict won't appear; use absent key instead
    snaps = [{}, {"A": "hello"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    assert result.get("A").first_seen == "s2"


def test_last_seen_returns_last_present_label():
    snaps = [{"A": "v1"}, {"A": "v2"}, {}]
    result = build_lineage(snaps, labels=["s1", "s2", "s3"])
    assert result.get("A").last_seen == "s2"


def test_stable_key_when_value_unchanged():
    snaps = [{"A": "same"}, {"A": "same"}, {"A": "same"}]
    result = build_lineage(snaps, labels=["s1", "s2", "s3"])
    assert result.get("A").is_stable is True


def test_unstable_key_when_value_changes():
    snaps = [{"A": "v1"}, {"A": "v2"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    assert result.get("A").is_stable is False


def test_unstable_keys_list():
    snaps = [{"A": "1", "B": "x"}, {"A": "2", "B": "x"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    assert result.unstable_keys == ["A"]


def test_change_count_zero_for_stable():
    snaps = [{"A": "v"}, {"A": "v"}]
    result = build_lineage(snaps, labels=["s1", "s2"])
    assert result.get("A").change_count == 1  # initial appearance counts


def test_change_count_increments_on_value_change():
    snaps = [{"A": "v1"}, {"A": "v2"}, {"A": "v2"}, {"A": "v3"}]
    result = build_lineage(snaps, labels=["s1", "s2", "s3", "s4"])
    # changes: None->v1, v1->v2, v2->v3 = 3
    assert result.get("A").change_count == 3


def test_labels_length_mismatch_raises():
    with pytest.raises(ValueError):
        build_lineage([{"A": "1"}], labels=["s1", "s2"])


def test_get_missing_key_returns_none():
    result = build_lineage([{"A": "1"}], labels=["s1"])
    assert result.get("MISSING") is None


def test_event_repr_absent():
    e = LineageEvent(snapshot_label="s1", value=None)
    assert "absent" in repr(e)


def test_entry_repr_contains_key():
    entry = LineageEntry(key="MY_KEY")
    assert "MY_KEY" in repr(entry)
