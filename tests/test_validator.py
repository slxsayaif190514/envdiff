"""Tests for envdiff.validator."""
import pytest
from envdiff.validator import validate_env, ValidationResult


@pytest.fixture
def base_env():
    return {
        "APP_PORT": "8080",
        "DEBUG": "true",
        "DATABASE_URL": "https://db.example.com",
        "APP_NAME": "myapp",
    }


def test_valid_env_no_schema(base_env):
    result = validate_env(base_env)
    assert result.is_valid
    assert result.issue_count == 0


def test_missing_required_key(base_env):
    result = validate_env(base_env, required=["APP_PORT", "SECRET_KEY"])
    assert not result.is_valid
    assert "SECRET_KEY" in result.missing_required
    assert "APP_PORT" not in result.missing_required


def test_all_required_present(base_env):
    result = validate_env(base_env, required=["APP_PORT", "DEBUG"])
    assert result.is_valid


def test_schema_type_int_valid(base_env):
    result = validate_env(base_env, schema={"APP_PORT": "int"})
    assert result.is_valid
    assert not result.type_errors


def test_schema_type_int_invalid():
    env = {"APP_PORT": "not_a_number"}
    result = validate_env(env, schema={"APP_PORT": "int"})
    assert not result.is_valid
    assert "APP_PORT" in result.type_errors


def test_schema_type_bool_valid(base_env):
    result = validate_env(base_env, schema={"DEBUG": "bool"})
    assert result.is_valid


def test_schema_type_bool_invalid():
    env = {"DEBUG": "maybe"}
    result = validate_env(env, schema={"DEBUG": "bool"})
    assert "DEBUG" in result.type_errors


def test_schema_type_url_valid(base_env):
    result = validate_env(base_env, schema={"DATABASE_URL": "url"})
    assert result.is_valid


def test_schema_type_url_invalid():
    env = {"DATABASE_URL": "not-a-url"}
    result = validate_env(env, schema={"DATABASE_URL": "url"})
    assert "DATABASE_URL" in result.type_errors


def test_unknown_keys_flagged_when_disallowed(base_env):
    schema = {"APP_PORT": "int", "DEBUG": "bool"}
    result = validate_env(base_env, schema=schema, allow_unknown=False)
    assert "DATABASE_URL" in result.unknown_keys
    assert "APP_NAME" in result.unknown_keys


def test_unknown_keys_allowed_by_default(base_env):
    schema = {"APP_PORT": "int"}
    result = validate_env(base_env, schema=schema, allow_unknown=True)
    assert not result.unknown_keys


def test_missing_key_not_type_checked():
    env = {}
    result = validate_env(env, schema={"PORT": "int"})
    # key not present — no type error, only missing if required
    assert not result.type_errors


def test_issue_count_aggregates_all():
    env = {"PORT": "bad", "EXTRA": "x"}
    result = validate_env(
        env,
        required=["MISSING_KEY"],
        schema={"PORT": "int"},
        allow_unknown=False,
    )
    assert result.issue_count == 3  # 1 missing + 1 unknown + 1 type error
