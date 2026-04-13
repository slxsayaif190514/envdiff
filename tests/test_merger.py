"""Tests for envdiff.merger."""

import pytest
from envdiff.merger import MergeConflict, MergeResult, merge_envs


@pytest.fixture
def two_envs():
    a = ("a.env", {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"})
    b = ("b.env", {"HOST": "remotehost", "PORT": "5432", "SECRET": "abc"})
    return [a, b]


def test_merge_result_contains_all_keys(two_envs):
    result = merge_envs(two_envs)
    assert set(result.merged.keys()) == {"HOST", "PORT", "DEBUG", "SECRET"}


def test_merge_strategy_first_keeps_first_value(two_envs):
    result = merge_envs(two_envs, strategy="first")
    assert result.merged["HOST"] == "localhost"


def test_merge_strategy_last_keeps_last_value(two_envs):
    result = merge_envs(two_envs, strategy="last")
    assert result.merged["HOST"] == "remotehost"


def test_no_conflict_for_matching_values(two_envs):
    result = merge_envs(two_envs)
    assert "PORT" not in result.conflict_keys


def test_conflict_detected_for_differing_values(two_envs):
    result = merge_envs(two_envs)
    assert "HOST" in result.conflict_keys


def test_sources_recorded(two_envs):
    result = merge_envs(two_envs)
    assert result.sources == ["a.env", "b.env"]


def test_has_conflicts_true(two_envs):
    result = merge_envs(two_envs)
    assert result.has_conflicts is True


def test_has_conflicts_false():
    envs = [("x.env", {"A": "1"}), ("y.env", {"A": "1"})]
    result = merge_envs(envs)
    assert result.has_conflicts is False


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([("a.env", {})], strategy="random")


def test_single_env_no_conflicts():
    envs = [("only.env", {"FOO": "bar", "BAZ": "qux"})]
    result = merge_envs(envs)
    assert result.merged == {"FOO": "bar", "BAZ": "qux"}
    assert not result.has_conflicts


def test_conflict_repr():
    c = MergeConflict(key="HOST", values={"a.env": "localhost", "b.env": "remote"})
    r = repr(c)
    assert "HOST" in r
    assert "localhost" in r
