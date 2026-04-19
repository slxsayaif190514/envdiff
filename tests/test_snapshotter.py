"""Tests for envdiff.snapshotter."""
import json
import os
import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.snapshotter import (
    Snapshot,
    SnapshotError,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture()
def simple_result() -> CompareResult:
    return CompareResult(
        file_a=".env.staging",
        file_b=".env.prod",
        missing_in_b=[KeyDiff("DB_HOST", "missing_in_b", "localhost", None)],
        missing_in_a=[KeyDiff("NEW_FLAG", "missing_in_a", None, "true")],
        mismatches=[KeyDiff("LOG_LEVEL", "mismatch", "debug", "error")],
    )


def test_save_creates_file(tmp_path, simple_result):
    out = str(tmp_path / "snap.json")
    snap = save_snapshot(simple_result, label="v1", path=out)
    assert os.path.exists(out)
    assert snap.label == "v1"


def test_save_json_structure(tmp_path, simple_result):
    out = str(tmp_path / "snap.json")
    save_snapshot(simple_result, label="test", path=out)
    with open(out) as fh:
        data = json.load(fh)
    assert data["label"] == "test"
    assert data["file_a"] == ".env.staging"
    assert data["file_b"] == ".env.prod"
    assert len(data["diffs"]) == 3


def test_save_diff_types_present(tmp_path, simple_result):
    out = str(tmp_path / "snap.json")
    save_snapshot(simple_result, label="x", path=out)
    with open(out) as fh:
        data = json.load(fh)
    types = {d["type"] for d in data["diffs"]}
    assert types == {"missing_in_b", "missing_in_a", "mismatch"}


def test_load_roundtrip(tmp_path, simple_result):
    out = str(tmp_path / "snap.json")
    save_snapshot(simple_result, label="roundtrip", path=out)
    loaded = load_snapshot(out)
    assert loaded.label == "roundtrip"
    assert loaded.file_a == ".env.staging"
    assert len(loaded.diffs) == 3


def test_load_missing_file_raises():
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("/nonexistent/path/snap.json")


def test_save_bad_path_raises(simple_result):
    with pytest.raises(SnapshotError, match="Cannot write"):
        save_snapshot(simple_result, label="x", path="/no/such/dir/snap.json")


def test_load_corrupt_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{{{")
    with pytest.raises(SnapshotError, match="Cannot read"):
        load_snapshot(str(bad))


def test_snapshot_no_diffs(tmp_path):
    result = CompareResult(
        file_a="a", file_b="b",
        missing_in_b=[], missing_in_a=[], mismatches=[]
    )
    out = str(tmp_path / "empty.json")
    snap = save_snapshot(result, label="empty", path=out)
    assert snap.diffs == []
    loaded = load_snapshot(out)
    assert loaded.diffs == []


def test_load_roundtrip_diff_values(tmp_path, simple_result):
    """Check that key/value_a/value_b fields survive a save+load cycle."""
    out = str(tmp_path / "snap.json")
    save_snapshot(simple_result, label="values", path=out)
    loaded = load_snapshot(out)
    mismatch = next(d for d in loaded.diffs if d.type == "mismatch")
    assert mismatch.key == "LOG_LEVEL"
    assert mismatch.value_a == "debug"
    assert mismatch.value_b == "error"
