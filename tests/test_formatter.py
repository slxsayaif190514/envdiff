"""Tests for envdiff.formatter."""

import pytest
from envdiff.comparator import compare_envs
from envdiff.formatter import format_result


def _result(a, b, **kwargs):
    return compare_envs(a, b, env_a_name=".env.dev", env_b_name=".env.prod", **kwargs)


def test_no_diff_message():
    result = _result({"A": "1"}, {"A": "1"})
    output = format_result(result, no_color=True)
    assert "No differences" in output


def test_missing_in_b_shown():
    result = _result({"DEBUG": "true", "HOST": "x"}, {"HOST": "x"})
    output = format_result(result, no_color=True)
    assert "DEBUG" in output
    assert ".env.dev" in output


def test_missing_in_a_shown():
    result = _result({"HOST": "x"}, {"HOST": "x", "SECRET": "s"})
    output = format_result(result, no_color=True)
    assert "SECRET" in output


def test_mismatch_shown():
    result = _result({"HOST": "localhost"}, {"HOST": "prod.example.com"})
    output = format_result(result, no_color=True)
    assert "HOST" in output
    assert "localhost" in output
    assert "prod.example.com" in output


def test_total_count_in_output():
    result = _result({"A": "1", "B": "2"}, {"A": "9"})
    output = format_result(result, no_color=True)
    assert "Total differences" in output


def test_env_names_in_header():
    result = _result({}, {})
    output = format_result(result, no_color=True)
    # no-diff path just shows a success line, but both names are there
    assert ".env.dev" in output
    assert ".env.prod" in output
