"""Tests for envdiff.differ_symmetry."""
import pytest
from envdiff.differ_symmetry import compute_symmetry, SymmetryEntry, SymmetryResult


def test_identical_envs_are_symmetric():
    env = {"A": "1", "B": "2"}
    result = compute_symmetry(env, env)
    assert result.is_symmetric
    assert result.symmetry_ratio == 1.0


def test_disjoint_envs_zero_symmetry():
    result = compute_symmetry({"A": "1"}, {"B": "2"})
    assert result.symmetry_ratio == 0.0
    assert not result.is_symmetric


def test_partial_overlap():
    result = compute_symmetry({"A": "1", "B": "2"}, {"B": "2", "C": "3"})
    # total unique = 3, shared = 1
    assert result.total_keys == 3
    assert len(result.shared_keys) == 1
    assert result.shared_keys[0].key == "B"
    assert pytest.approx(result.symmetry_ratio) == 1 / 3


def test_exclusive_a_keys():
    result = compute_symmetry({"X": "1", "Y": "2"}, {"Y": "2"})
    assert len(result.exclusive_a) == 1
    assert result.exclusive_a[0].key == "X"


def test_exclusive_b_keys():
    result = compute_symmetry({"Y": "2"}, {"Y": "2", "Z": "3"})
    assert len(result.exclusive_b) == 1
    assert result.exclusive_b[0].key == "Z"


def test_entries_sorted_alphabetically():
    result = compute_symmetry({"C": "1", "A": "2"}, {"B": "3"})
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_values_stored_correctly():
    result = compute_symmetry({"K": "hello"}, {"K": "world"})
    entry = result.entries[0]
    assert entry.value_a == "hello"
    assert entry.value_b == "world"
    assert entry.is_shared
    assert not entry.values_match


def test_empty_envs_are_symmetric():
    result = compute_symmetry({}, {})
    assert result.is_symmetric
    assert result.total_keys == 0


def test_file_names_stored():
    result = compute_symmetry({}, {}, file_a="prod.env", file_b="dev.env")
    assert result.file_a == "prod.env"
    assert result.file_b == "dev.env"


def test_is_exclusive_flags():
    result = compute_symmetry({"A": "1"}, {"B": "2"})
    a_entry = next(e for e in result.entries if e.key == "A")
    b_entry = next(e for e in result.entries if e.key == "B")
    assert a_entry.is_exclusive_a
    assert not a_entry.is_exclusive_b
    assert b_entry.is_exclusive_b
    assert not b_entry.is_exclusive_a
