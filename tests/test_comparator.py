"""Tests for envdiff.comparator."""

import pytest
from envdiff.comparator import compare_envs, CompareResult, KeyDiff


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc123"}


def test_no_differences():
    result = compare_envs({"A": "1"}, {"A": "1"})
    assert not result.has_differences
    assert result.diffs == []


def test_missing_in_b():
    result = compare_envs(ENV_A, ENV_B)
    keys = [d.key for d in result.missing_in_b]
    assert "DEBUG" in keys


def test_missing_in_a():
    result = compare_envs(ENV_A, ENV_B)
    keys = [d.key for d in result.missing_in_a]
    assert "SECRET" in keys


def test_mismatch():
    result = compare_envs(ENV_A, ENV_B)
    mismatch_keys = [d.key for d in result.mismatches]
    assert "HOST" in mismatch_keys


def test_no_mismatch_same_value():
    result = compare_envs(ENV_A, ENV_B)
    mismatch_keys = [d.key for d in result.mismatches]
    assert "PORT" not in mismatch_keys


def test_keys_only_skips_value_diff():
    result = compare_envs(ENV_A, ENV_B, keys_only=True)
    assert result.mismatches == []
    # missing keys should still be reported
    assert len(result.missing_in_b) > 0 or len(result.missing_in_a) > 0


def test_env_names_in_result():
    result = compare_envs({}, {}, env_a_name=".env.dev", env_b_name=".env.prod")
    assert result.env_a_name == ".env.dev"
    assert result.env_b_name == ".env.prod"


def test_diffs_sorted_alphabetically():
    a = {"ZEBRA": "1", "APPLE": "2"}
    b = {"MANGO": "3"}
    result = compare_envs(a, b)
    keys = [d.key for d in result.diffs]
    assert keys == sorted(keys)


def test_key_diff_repr_mismatch():
    d = KeyDiff(key="FOO", status="mismatch", env_a_value="bar", env_b_value="baz")
    assert "mismatch" in repr(d)
    assert "FOO" in repr(d)


def test_key_diff_repr_missing():
    d = KeyDiff(key="FOO", status="missing_in_b", env_a_value="bar")
    assert "missing_in_b" in repr(d)
