"""Tests for envdiff.matrix_formatter."""
import re
import pytest
from envdiff.differ_matrix import build_matrix
from envdiff.matrix_formatter import format_matrix_result


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_C = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "xyz"}


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_header_shows_file_count():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    out = _strip(format_matrix_result(result))
    assert "2 file" in out


def test_header_shows_pair_count():
    result = build_matrix({"a": ENV_A, "b": ENV_B, "c": ENV_C})
    out = _strip(format_matrix_result(result))
    assert "3 pair" in out


def test_clean_pair_shows_no_differences():
    result = build_matrix({"a": ENV_A, "b": ENV_B})
    out = _strip(format_matrix_result(result))
    assert "no differences" in out


def test_dirty_pair_shows_issue_count():
    result = build_matrix({"a": ENV_A, "c": ENV_C})
    out = _strip(format_matrix_result(result))
    assert "issue" in out


def test_file_names_appear_in_output():
    result = build_matrix({"dev.env": ENV_A, "prod.env": ENV_C})
    out = _strip(format_matrix_result(result))
    assert "dev.env" in out
    assert "prod.env" in out


def test_empty_matrix_shows_no_pairs_message():
    result = build_matrix({})
    out = _strip(format_matrix_result(result))
    assert "No pairs" in out


def test_summary_line_present():
    result = build_matrix({"a": ENV_A, "b": ENV_B, "c": ENV_C})
    out = _strip(format_matrix_result(result))
    assert "clean" in out
    assert "issues" in out
