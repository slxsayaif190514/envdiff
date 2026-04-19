import pytest
from envdiff.splitter import split_env, to_env_dict, SplitResult


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envdiff",
        "APP_ENV": "production",
        "SECRET": "abc123",
    }


def test_split_returns_result(sample_env):
    result = split_env(sample_env, filename="test.env")
    assert isinstance(result, SplitResult)
    assert result.source == "test.env"


def test_total_keys_matches_env(sample_env):
    result = split_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_db_prefix_grouped(sample_env):
    result = split_env(sample_env)
    assert "DB" in result.groups
    assert result.keys_for("DB") == ["DB_HOST", "DB_PORT"] or set(result.keys_for("DB")) == {"DB_HOST", "DB_PORT"}


def test_app_prefix_grouped(sample_env):
    result = split_env(sample_env)
    assert "APP" in result.groups
    assert set(result.keys_for("APP")) == {"APP_NAME", "APP_ENV"}


def test_key_without_separator_goes_to_other(sample_env):
    result = split_env(sample_env)
    assert "__OTHER__" in result.groups
    assert "SECRET" in result.keys_for("__OTHER__")


def test_group_count(sample_env):
    result = split_env(sample_env)
    assert result.group_count == 3  # DB, APP, __OTHER__


def test_filter_by_prefixes(sample_env):
    result = split_env(sample_env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "APP" not in result.groups
    assert "__OTHER__" in result.groups


def test_to_env_dict(sample_env):
    result = split_env(sample_env)
    d = to_env_dict(result, "DB")
    assert d["DB_HOST"] == "localhost"
    assert d["DB_PORT"] == "5432"


def test_to_env_dict_missing_prefix(sample_env):
    result = split_env(sample_env)
    assert to_env_dict(result, "NONEXISTENT") == {}


def test_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "NOPE": "x"}
    result = split_env(env, separator=".")
    assert "DB" in result.groups
    assert len(result.keys_for("DB")) == 2
