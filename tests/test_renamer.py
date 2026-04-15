"""Tests for envdiff.renamer."""

import pytest
from envdiff.renamer import rename_keys, RenameResult, RenameConflict


@pytest.fixture
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_SECRET": "abc123"}


def test_rename_single_key(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "DB_HOST" not in result.env
    assert result.env["DATABASE_HOST"] == "localhost"


def test_rename_preserves_other_keys(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_PORT" in result.env
    assert "APP_SECRET" in result.env


def test_rename_count(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert result.rename_count == 2


def test_renamed_list_contains_pairs(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.renamed


def test_missing_source_key_creates_conflict(base_env):
    result = rename_keys(base_env, {"NONEXISTENT": "NEW_KEY"})
    assert result.has_conflicts
    conflict = result.skipped[0]
    assert conflict.old_key == "NONEXISTENT"
    assert "not found" in conflict.reason


def test_target_key_exists_creates_conflict(base_env):
    # DB_PORT already exists; renaming DB_HOST -> DB_PORT should conflict
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"})
    assert result.has_conflicts
    assert result.skipped[0].new_key == "DB_PORT"
    assert "already exists" in result.skipped[0].reason


def test_overwrite_flag_resolves_conflict(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DB_PORT"}, overwrite=True)
    assert not result.has_conflicts
    assert result.env["DB_PORT"] == "localhost"


def test_no_conflicts_has_conflicts_false(base_env):
    result = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert not result.has_conflicts


def test_empty_mapping_returns_unchanged(base_env):
    result = rename_keys(base_env, {})
    assert result.env == base_env
    assert result.rename_count == 0
    assert not result.has_conflicts


def test_original_env_not_mutated(base_env):
    original_copy = dict(base_env)
    rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert base_env == original_copy
