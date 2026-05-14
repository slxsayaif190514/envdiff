"""Tests for envdiff.differ_variance."""

import pytest

from envdiff.differ_variance import VarianceEntry, VarianceResult, build_variance


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.db", "PORT": "5432", "DEBUG": "false"}
ENV_C = {"HOST": "staging.db", "PORT": "5432", "DEBUG": "false", "EXTRA": "only_c"}


# ---------------------------------------------------------------------------
# build_variance
# ---------------------------------------------------------------------------

def test_build_variance_key_count():
    result = build_variance([ENV_A, ENV_B], ["a.env", "b.env"])
    assert result.key_count == 3


def test_build_variance_filenames_stored():
    result = build_variance([ENV_A, ENV_B], ["a.env", "b.env"])
    assert result.filenames == ["a.env", "b.env"]


def test_build_variance_uniform_key():
    result = build_variance([ENV_A, ENV_B], ["a.env", "b.env"])
    entry = result.get("PORT")
    assert entry is not None
    assert entry.is_uniform
    assert entry.variance_count == 1


def test_build_variance_variant_key():
    result = build_variance([ENV_A, ENV_B], ["a.env", "b.env"])
    entry = result.get("HOST")
    assert entry is not None
    assert not entry.is_uniform
    assert entry.variance_count == 2


def test_build_variance_missing_key_in_one_env():
    result = build_variance([ENV_A, ENV_C], ["a.env", "c.env"])
    entry = result.get("EXTRA")
    assert entry is not None
    # present in c.env, missing (None) in a.env
    assert entry.values["a.env"] is None
    assert entry.values["c.env"] == "only_c"
    assert not entry.is_uniform


def test_build_variance_three_envs_uniform_port():
    result = build_variance([ENV_A, ENV_B, ENV_C], ["a", "b", "c"])
    entry = result.get("PORT")
    assert entry is not None
    assert entry.is_uniform


def test_build_variance_is_uniform_flag():
    env_x = {"KEY": "same"}
    env_y = {"KEY": "same"}
    result = build_variance([env_x, env_y], ["x", "y"])
    assert result.is_uniform
    assert result.variant_count == 0
    assert result.uniform_count == 1


def test_build_variance_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        build_variance([ENV_A], ["a", "b"])


def test_build_variance_get_missing_key_returns_none():
    result = build_variance([ENV_A], ["a"])
    assert result.get("NONEXISTENT") is None


def test_build_variance_keys_sorted_alphabetically():
    result = build_variance([ENV_A], ["a"])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_build_variance_variant_count_three_distinct():
    ea = {"MODE": "dev"}
    eb = {"MODE": "staging"}
    ec = {"MODE": "prod"}
    result = build_variance([ea, eb, ec], ["a", "b", "c"])
    entry = result.get("MODE")
    assert entry is not None
    assert entry.variance_count == 3
