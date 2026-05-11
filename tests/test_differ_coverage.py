"""Tests for differ_coverage module."""
import pytest
from envdiff.differ_coverage import compute_coverage, CoverageEntry, CoverageResult


@pytest.fixture()
def three_envs():
    return {
        "dev.env": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging.env": {"DB_HOST": "staging-db", "DB_PORT": "5432", "LOG_LEVEL": "info"},
        "prod.env": {"DB_HOST": "prod-db", "DB_PORT": "5432"},
    }


def test_result_is_coverage_result(three_envs):
    result = compute_coverage(three_envs)
    assert isinstance(result, CoverageResult)


def test_filenames_stored(three_envs):
    result = compute_coverage(three_envs)
    assert set(result.filenames) == {"dev.env", "staging.env", "prod.env"}


def test_key_count_equals_unique_keys(three_envs):
    result = compute_coverage(three_envs)
    assert result.key_count == 4  # DB_HOST, DB_PORT, DEBUG, LOG_LEVEL


def test_universal_key_present_in_all(three_envs):
    result = compute_coverage(three_envs)
    assert "DB_HOST" in result.universal_keys
    assert "DB_PORT" in result.universal_keys


def test_non_universal_key_not_in_universal(three_envs):
    result = compute_coverage(three_envs)
    assert "DEBUG" not in result.universal_keys
    assert "LOG_LEVEL" not in result.universal_keys


def test_orphan_key_detected(three_envs):
    result = compute_coverage(three_envs)
    assert "DEBUG" in result.orphan_keys
    assert "LOG_LEVEL" in result.orphan_keys


def test_coverage_ratio_universal():
    envs = {"a.env": {"X": "1"}, "b.env": {"X": "2"}}
    result = compute_coverage(envs)
    entry = result.entries[0]
    assert entry.coverage_ratio == 1.0
    assert entry.is_universal


def test_coverage_ratio_partial():
    envs = {"a.env": {"X": "1"}, "b.env": {}, "c.env": {}}
    result = compute_coverage(envs)
    entry = next(e for e in result.entries if e.key == "X")
    assert abs(entry.coverage_ratio - 1 / 3) < 0.001


def test_absent_in_populated_correctly(three_envs):
    result = compute_coverage(three_envs)
    debug_entry = next(e for e in result.entries if e.key == "DEBUG")
    assert "dev.env" in debug_entry.present_in
    assert "staging.env" in debug_entry.absent_in
    assert "prod.env" in debug_entry.absent_in


def test_average_coverage_all_universal():
    envs = {"a.env": {"K": "1"}, "b.env": {"K": "2"}}
    result = compute_coverage(envs)
    assert result.average_coverage == 1.0


def test_average_coverage_partial():
    envs = {"a.env": {"X": "1", "Y": "2"}, "b.env": {"X": "1"}}
    result = compute_coverage(envs)
    # X: 2/2=1.0, Y: 1/2=0.5 -> avg = 0.75
    assert abs(result.average_coverage - 0.75) < 0.001


def test_empty_envs_returns_empty_result():
    result = compute_coverage({})
    assert result.key_count == 0
    assert result.average_coverage == 1.0


def test_entries_sorted_alphabetically(three_envs):
    result = compute_coverage(three_envs)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_repr_coverage_entry():
    e = CoverageEntry(key="FOO", present_in=["a"], absent_in=["b"])
    assert "FOO" in repr(e)
