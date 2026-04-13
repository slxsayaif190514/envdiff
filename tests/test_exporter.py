"""Tests for envdiff.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.exporter import export_csv, export_json, export_result


def _diff(key: str, a: str | None = None, b: str | None = None) -> KeyDiff:
    return KeyDiff(key=key, value_a=a, value_b=b)


@pytest.fixture()
def full_result() -> CompareResult:
    return CompareResult(
        missing_in_b=[_diff("ONLY_A", a="hello")],
        missing_in_a=[_diff("ONLY_B", b="world")],
        mismatches=[_diff("SHARED", a="old", b="new")],
    )


# --- JSON ---

def test_export_json_structure(full_result: CompareResult) -> None:
    raw = export_json(full_result)
    data = json.loads(raw)
    assert set(data.keys()) == {"missing_in_b", "missing_in_a", "mismatches"}


def test_export_json_missing_in_b(full_result: CompareResult) -> None:
    data = json.loads(export_json(full_result))
    assert data["missing_in_b"] == [{"key": "ONLY_A", "value_a": "hello"}]


def test_export_json_missing_in_a(full_result: CompareResult) -> None:
    data = json.loads(export_json(full_result))
    assert data["missing_in_a"] == [{"key": "ONLY_B", "value_b": "world"}]


def test_export_json_mismatches(full_result: CompareResult) -> None:
    data = json.loads(export_json(full_result))
    assert data["mismatches"] == [{"key": "SHARED", "value_a": "old", "value_b": "new"}]


def test_export_json_empty() -> None:
    empty = CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[])
    data = json.loads(export_json(empty))
    assert data == {"missing_in_b": [], "missing_in_a": [], "mismatches": []}


# --- CSV ---

def test_export_csv_headers(full_result: CompareResult) -> None:
    rows = list(csv.reader(io.StringIO(export_csv(full_result))))
    assert rows[0] == ["type", "key", "value_a", "value_b"]


def test_export_csv_row_count(full_result: CompareResult) -> None:
    rows = list(csv.reader(io.StringIO(export_csv(full_result))))
    # header + 3 data rows
    assert len(rows) == 4


def test_export_csv_mismatch_row(full_result: CompareResult) -> None:
    rows = list(csv.reader(io.StringIO(export_csv(full_result))))
    mismatch_rows = [r for r in rows if r[0] == "mismatch"]
    assert mismatch_rows == [["mismatch", "SHARED", "old", "new"]]


# --- dispatch ---

def test_export_result_json(full_result: CompareResult) -> None:
    out = export_result(full_result, "json")
    assert json.loads(out)  # valid JSON


def test_export_result_csv(full_result: CompareResult) -> None:
    out = export_result(full_result, "csv")
    assert "type" in out


def test_export_result_invalid_format(full_result: CompareResult) -> None:
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_result(full_result, "xml")  # type: ignore[arg-type]
