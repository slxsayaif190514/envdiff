import pytest
from envdiff.trimmer import trim_env, TrimResult


@pytest.fixture
def ref():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod"}


def test_all_keys_in_reference_kept(ref):
    env = {"DB_HOST": "db", "DB_PORT": "5432", "APP_ENV": "dev"}
    result = trim_env(env, ref, filename="app.env")
    assert result.is_clean
    assert result.removed == []
    assert set(result.kept) == {"DB_HOST", "DB_PORT", "APP_ENV"}


def test_extra_keys_removed(ref):
    env = {"DB_HOST": "db", "EXTRA_KEY": "val", "APP_ENV": "dev"}
    result = trim_env(env, ref)
    assert not result.is_clean
    assert "EXTRA_KEY" in result.removed
    assert "DB_HOST" in result.kept


def test_removed_count(ref):
    env = {"A": "1", "B": "2", "DB_HOST": "x"}
    result = trim_env(env, ref)
    assert result.removed_count == 2


def test_removed_keys_sorted(ref):
    env = {"Z_KEY": "z", "A_KEY": "a", "DB_HOST": "x"}
    result = trim_env(env, ref)
    assert result.removed == ["A_KEY", "Z_KEY"]


def test_empty_env(ref):
    result = trim_env({}, ref, filename="empty.env")
    assert result.is_clean
    assert result.kept == {}


def test_empty_reference():
    env = {"KEY": "val"}
    result = trim_env(env, {})
    assert result.removed == ["KEY"]
    assert result.kept == {}


def test_filename_stored():
    result = trim_env({}, {}, filename="test.env")
    assert result.filename == "test.env"


def test_repr_does_not_crash():
    result = trim_env({"A": "1"}, {"A": "1"})
    assert "TrimResult" in repr(result)
