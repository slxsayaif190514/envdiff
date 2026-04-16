"""Tests for envdiff.pinner."""
import json
import pytest
from pathlib import Path
from envdiff.pinner import (
    PinError,
    PinEntry,
    PinResult,
    save_pin,
    load_pin,
    check_pin,
)


def test_pin_entry_not_drifted():
    e = PinEntry("KEY", "val", "val")
    assert not e.drifted


def test_pin_entry_drifted_changed():
    e = PinEntry("KEY", "old", "new")
    assert e.drifted


def test_pin_entry_drifted_removed():
    e = PinEntry("KEY", "old", None)
    assert e.drifted


def test_save_and_load_pin(tmp_path):
    p = tmp_path / "pin.json"
    env = {"A": "1", "B": "2"}
    save_pin(env, p)
    loaded = load_pin(p)
    assert loaded == env


def test_load_pin_missing_file_raises(tmp_path):
    with pytest.raises(PinError):
        load_pin(tmp_path / "missing.json")


def test_save_pin_bad_path_raises():
    with pytest.raises(PinError):
        save_pin({"K": "v"}, Path("/no/such/dir/pin.json"))


def test_check_pin_clean():
    pinned = {"A": "1", "B": "2"}
    current = {"A": "1", "B": "2"}
    result = check_pin(pinned, current, "test.env")
    assert result.is_clean
    assert result.drift_count == 0
    assert result.drifted_keys == []


def test_check_pin_changed_value():
    pinned = {"A": "1"}
    current = {"A": "changed"}
    result = check_pin(pinned, current, "test.env")
    assert not result.is_clean
    assert result.drift_count == 1
    assert "A" in result.drifted_keys


def test_check_pin_removed_key():
    pinned = {"A": "1", "B": "2"}
    current = {"A": "1"}
    result = check_pin(pinned, current, "test.env")
    assert result.drift_count == 1
    assert "B" in result.drifted_keys


def test_check_pin_new_key_in_current_ignored():
    pinned = {"A": "1"}
    current = {"A": "1", "NEW": "x"}
    result = check_pin(pinned, current, "test.env")
    assert result.is_clean


def test_pin_result_filename():
    result = check_pin({}, {}, "prod.env")
    assert result.filename == "prod.env"
