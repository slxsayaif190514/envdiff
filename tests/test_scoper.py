import pytest
from envdiff.scoper import ScopeEntry, ScopeResult, scope_env, filter_to_scope


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "abc",
        "LOG_LEVEL": "info",
    }


def test_scope_result_filename_and_name(sample_env):
    result = scope_env(sample_env, ["DB_HOST"], scope_name="db", filename=".env")
    assert result.filename == ".env"
    assert result.scope_name == "db"


def test_total_count_equals_env_size(sample_env):
    result = scope_env(sample_env, ["DB_HOST"])
    assert result.total_count == len(sample_env)


def test_in_scope_keys_matched(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope_name="db")
    assert sorted(result.in_scope_keys) == ["DB_HOST", "DB_PORT"]


def test_out_of_scope_keys(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"])
    assert sorted(result.out_of_scope_keys) == ["APP_SECRET", "LOG_LEVEL"]


def test_in_scope_count(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "APP_SECRET"])
    assert result.in_scope_count == 2


def test_empty_scope_keys(sample_env):
    result = scope_env(sample_env, [])
    assert result.in_scope_count == 0
    assert result.out_of_scope_keys == sorted(sample_env.keys())


def test_all_keys_in_scope(sample_env):
    result = scope_env(sample_env, list(sample_env.keys()))
    assert result.in_scope_count == result.total_count
    assert result.out_of_scope_keys == []


def test_unknown_scope_key_ignored(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "NONEXISTENT"])
    assert result.in_scope_count == 1
    assert "DB_HOST" in result.in_scope_keys


def test_filter_to_scope_returns_only_in_scope(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "LOG_LEVEL"])
    filtered = filter_to_scope(result)
    assert set(filtered.keys()) == {"DB_HOST", "LOG_LEVEL"}


def test_filter_to_scope_values_preserved(sample_env):
    result = scope_env(sample_env, ["DB_PORT"])
    filtered = filter_to_scope(result)
    assert filtered["DB_PORT"] == "5432"


def test_entries_sorted_by_key(sample_env):
    result = scope_env(sample_env, [])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
