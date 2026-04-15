"""Tests for envdiff.redactor."""

import pytest
from envdiff.redactor import redact_env, RedactResult, DEFAULT_PLACEHOLDER


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
        "DEBUG": "true",
        "PRIVATE_KEY": "-----BEGIN RSA",
    }


def test_non_sensitive_keys_unchanged(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"
    assert result.redacted["DEBUG"] == "true"


def test_sensitive_keys_redacted(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_PLACEHOLDER
    assert result.redacted["API_KEY"] == DEFAULT_PLACEHOLDER
    assert result.redacted["AUTH_TOKEN"] == DEFAULT_PLACEHOLDER
    assert result.redacted["PRIVATE_KEY"] == DEFAULT_PLACEHOLDER


def test_redact_count(sample_env):
    result = redact_env(sample_env)
    assert result.redact_count == 4


def test_redacted_keys_sorted(sample_env):
    result = redact_env(sample_env)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_original_preserved(sample_env):
    result = redact_env(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"
    assert result.original["API_KEY"] == "abc123"


def test_is_clean_when_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env(env)
    assert result.is_clean
    assert result.redact_count == 0


def test_custom_placeholder(sample_env):
    result = redact_env(sample_env, placeholder="<hidden>")
    assert result.redacted["DB_PASSWORD"] == "<hidden>"


def test_extra_keys_redacted():
    env = {"MY_CUSTOM": "value", "NORMAL": "ok"}
    result = redact_env(env, extra_keys=["MY_CUSTOM"])
    assert result.redacted["MY_CUSTOM"] == DEFAULT_PLACEHOLDER
    assert result.redacted["NORMAL"] == "ok"


def test_extra_patterns_redacted():
    env = {"STRIPE_LIVE_KEY": "sk_live_abc", "SAFE": "yes"}
    result = redact_env(env, extra_patterns=[r"stripe"])
    assert result.redacted["STRIPE_LIVE_KEY"] == DEFAULT_PLACEHOLDER
    assert result.redacted["SAFE"] == "yes"


def test_empty_env():
    result = redact_env({})
    assert result.redacted == {}
    assert result.is_clean
