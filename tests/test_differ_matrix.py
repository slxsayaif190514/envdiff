"""Tests for envdiff.differ_matrix."""
import pytest
from envdiff.differ_matrix import build_matrix, MatrixCell, MatrixResult


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_C = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "xyz"}


def test_build_matrix_pair_count():
    result = build_matrix({"a": ENV_A, "b": ENV_B, "c": ENV_C})
    assert result.pair_count == 3  # (a,b), (a,c), (b,c)


def test_build_matrix_files_list():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.files == ["a", "b"]


def test_identical_envs_no_issues():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    cell = result.get("a", "b")
    assert cell is not None
    assert not cell.has_issues


def test_different_envs_have_issues():
    result = build_matrix({"a": ENV_A, "c": ENV_C})
    cell = result.get("a", "c")
    assert cell is not None
    assert cell.has_issues


def test_issue_count_correct():
    result = build_matrix({"a": ENV_A, "c": ENV_C})
    cell = result.get("a", "c")
    # missing_in_b: SECRET not in A; missing_in_a: DEBUG not in C; mismatches: HOST differs
    assert cell.issue_count == 3


def test_clean_pairs_and_dirty_pairs():
    result = build_matrix({"a": ENV_A, "b": ENV_B, "c": ENV_C})
    assert len(result.clean_pairs) == 1
    assert len(result.dirty_pairs) == 2


def test_get_returns_none_for_unknown_pair():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    assert result.get("x", "y") is None


def test_empty_input_returns_empty_matrix():
    result = build_matrix({})
    assert result.pair_count == 0
    assert result.files == []


def test_single_env_no_pairs():
    result = build_matrix({"only": ENV_A})
    assert result.pair_count == 0


def test_matrix_cell_repr_does_not_raise():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    cell = result.cells[0]
    assert "a" in repr(cell)
