import pytest
from envdiff.classifier import classify_env, UNCATEGORIZED


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "DB_PASSWORD": "secret",
        "API_KEY": "abc123",
        "JWT_SECRET": "supersecret",
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "LOG_LEVEL": "info",
        "FEATURE_DARK_MODE": "true",
        "S3_BUCKET": "my-bucket",
        "SMTP_HOST": "mail.example.com",
        "APP_NAME": "myapp",
    }


def test_classify_returns_result(sample_env):
    result = classify_env(sample_env, filename=".env")
    assert result.filename == ".env"


def test_database_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "DATABASE_URL" in result.keys_in("database")
    assert "DB_PASSWORD" in result.keys_in("database")


def test_auth_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "API_KEY" in result.keys_in("auth")
    assert "JWT_SECRET" in result.keys_in("auth")


def test_network_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "APP_HOST" in result.keys_in("network")
    assert "APP_PORT" in result.keys_in("network")


def test_logging_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "LOG_LEVEL" in result.keys_in("logging")


def test_feature_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "FEATURE_DARK_MODE" in result.keys_in("feature")


def test_storage_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "S3_BUCKET" in result.keys_in("storage")


def test_email_keys_classified(sample_env):
    result = classify_env(sample_env)
    assert "SMTP_HOST" in result.keys_in("email")


def test_uncategorized_key(sample_env):
    result = classify_env(sample_env)
    assert "APP_NAME" in result.keys_in(UNCATEGORIZED)


def test_total_keys(sample_env):
    result = classify_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_category_count(sample_env):
    result = classify_env(sample_env)
    assert result.category_count >= 7


def test_empty_env():
    result = classify_env({})
    assert result.total_keys == 0
    assert result.category_count == 0
