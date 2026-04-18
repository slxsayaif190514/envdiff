import pytest
from envdiff.normalizer import normalize_env, NormalizeResult


@pytest.fixture
def clean_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_clean_env_no_changes(clean_env):
    result = normalize_env(clean_env, "prod.env")
    assert result.is_clean
    assert result.change_count == 0


def test_filename_stored(clean_env):
    result = normalize_env(clean_env, "staging.env")
    assert result.filename == "staging.env"


def test_whitespace_stripped():
    env = {"KEY": "  hello  "}
    result = normalize_env(env)
    assert result.normalized["KEY"] == "hello"
    assert result.change_count == 1


def test_boolean_true_lowercased():
    env = {"FLAG": "True"}
    result = normalize_env(env)
    assert result.normalized["FLAG"] == "true"


def test_boolean_false_lowercased():
    env = {"FLAG": "FALSE"}
    result = normalize_env(env)
    assert result.normalized["FLAG"] == "false"


def test_yes_no_normalized():
    env = {"ENABLED": "YES", "ACTIVE": "No"}
    result = normalize_env(env)
    assert result.normalized["ENABLED"] == "yes"
    assert result.normalized["ACTIVE"] == "no"


def test_on_off_normalized():
    env = {"FEATURE": "ON", "LEGACY": "Off"}
    result = normalize_env(env)
    assert result.normalized["FEATURE"] == "on"
    assert result.normalized["LEGACY"] == "off"


def test_changes_record_key_and_values():
    env = {"DEBUG": "TRUE"}
    result = normalize_env(env)
    assert len(result.changes) == 1
    key, before, after = result.changes[0]
    assert key == "DEBUG"
    assert before == "TRUE"
    assert after == "true"


def test_original_preserved():
    env = {"KEY": "  VALUE  "}
    result = normalize_env(env)
    assert result.original["KEY"] == "  VALUE  "
    assert result.normalized["KEY"] == "VALUE"


def test_multiple_changes_counted():
    env = {"A": "  x  ", "B": "TRUE", "C": "clean"}
    result = normalize_env(env)
    assert result.change_count == 2
    assert not result.is_clean


def test_repr_contains_filename():
    result = normalize_env({}, "test.env")
    assert "test.env" in repr(result)
