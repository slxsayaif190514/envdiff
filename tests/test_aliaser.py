"""Tests for envdiff.aliaser and envdiff.aliaser_formatter."""
import pytest
from envdiff.aliaser import apply_aliases, AliasEntry, AliasResult
from envdiff.aliaser_formatter import format_alias_result


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "hunter2",
        "DEBUG": "true",
    }


def test_no_aliases_returns_all_unmapped(base_env):
    result = apply_aliases(base_env, {}, source_file="test.env")
    assert result.unmapped == base_env
    assert result.entries == []
    assert result.is_clean


def test_alias_found_key(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"}, source_file="a.env")
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.old_key == "DB_HOST"
    assert entry.new_key == "DATABASE_HOST"
    assert entry.value == "localhost"
    assert entry.found is True


def test_alias_missing_key(base_env):
    result = apply_aliases(base_env, {"OLD_KEY": "NEW_KEY"})
    assert result.missing_count == 1
    assert result.is_clean is False
    entry = result.entries[0]
    assert entry.found is False
    assert entry.value is None


def test_unmapped_keys_excluded_from_aliases(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" not in result.unmapped
    assert "DB_PORT" in result.unmapped
    assert "DEBUG" in result.unmapped


def test_to_dict_replaces_old_key_with_new(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"})
    d = result.to_dict()
    assert "DATABASE_HOST" in d
    assert d["DATABASE_HOST"] == "localhost"
    assert "DB_HOST" not in d


def test_to_dict_missing_alias_not_included(base_env):
    result = apply_aliases(base_env, {"MISSING": "NEW_MISSING"})
    d = result.to_dict()
    assert "NEW_MISSING" not in d
    assert "MISSING" not in d


def test_resolved_count(base_env):
    aliases = {"DB_HOST": "DATABASE_HOST", "NOPE": "STILL_NOPE"}
    result = apply_aliases(base_env, aliases)
    assert result.resolved_count == 1
    assert result.missing_count == 1


def test_entries_sorted_by_old_key(base_env):
    aliases = {"DB_PORT": "DATABASE_PORT", "APP_SECRET": "APPLICATION_SECRET"}
    result = apply_aliases(base_env, aliases)
    keys = [e.old_key for e in result.entries]
    assert keys == sorted(keys)


# --- formatter tests ---

def test_format_no_aliases_shows_message():
    result = AliasResult(source_file="empty.env")
    out = format_alias_result(result, color=False)
    assert "No aliases defined" in out
    assert "empty.env" in out


def test_format_resolved_shows_checkmark(base_env):
    result = apply_aliases(base_env, {"DB_HOST": "DATABASE_HOST"}, source_file="x.env")
    out = format_alias_result(result, color=False)
    assert "DB_HOST -> DATABASE_HOST" in out
    assert "1/1 aliases resolved" in out


def test_format_missing_shows_cross():
    result = apply_aliases({"A": "1"}, {"MISSING": "NEW"}, source_file="y.env")
    out = format_alias_result(result, color=False)
    assert "MISSING -> NEW" in out
    assert "[old key not found]" in out
    assert "0/1 aliases resolved" in out
