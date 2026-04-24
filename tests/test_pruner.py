"""Tests for envdiff.pruner."""

import pytest

from envdiff.pruner import PruneEntry, PruneResult, prune_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "info",
    }


def test_no_rules_keeps_all_keys(sample_env):
    result = prune_env(sample_env, "test.env")
    assert result.kept == sample_env
    assert result.removed == []


def test_is_clean_when_nothing_removed(sample_env):
    result = prune_env(sample_env, "test.env")
    assert result.is_clean is True


def test_exact_match_removes_key(sample_env):
    result = prune_env(sample_env, "test.env", exact=["LOG_LEVEL"])
    assert "LOG_LEVEL" not in result.kept
    assert result.removed_count == 1
    assert result.removed[0].key == "LOG_LEVEL"
    assert result.removed[0].reason == "exact"


def test_exact_match_preserves_other_keys(sample_env):
    result = prune_env(sample_env, "test.env", exact=["DB_HOST"])
    assert "DB_PORT" in result.kept
    assert "APP_SECRET" in result.kept


def test_pattern_removes_matching_keys(sample_env):
    result = prune_env(sample_env, "test.env", patterns=["DB_*"])
    assert "DB_HOST" not in result.kept
    assert "DB_PORT" not in result.kept
    assert result.removed_count == 2


def test_pattern_reason_is_pattern(sample_env):
    result = prune_env(sample_env, "test.env", patterns=["APP_*"])
    for entry in result.removed:
        assert entry.reason == "pattern"


def test_combined_exact_and_pattern(sample_env):
    result = prune_env(sample_env, "test.env", exact=["LOG_LEVEL"], patterns=["DB_*"])
    assert result.removed_count == 3
    assert "APP_SECRET" in result.kept
    assert "APP_DEBUG" in result.kept


def test_removed_keys_sorted(sample_env):
    result = prune_env(sample_env, "test.env", patterns=["*"])
    assert result.removed_keys == sorted(sample_env.keys())


def test_filename_stored(sample_env):
    result = prune_env(sample_env, "prod.env", exact=["DB_HOST"])
    assert result.filename == "prod.env"


def test_non_matching_pattern_keeps_all(sample_env):
    result = prune_env(sample_env, "test.env", patterns=["REDIS_*"])
    assert result.is_clean is True
    assert result.kept == sample_env


def test_removed_entry_value_preserved(sample_env):
    result = prune_env(sample_env, "test.env", exact=["DB_HOST"])
    entry = result.removed[0]
    assert entry.value == "localhost"
