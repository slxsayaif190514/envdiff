import pytest
from envdiff.masker import mask_env, MaskResult, MASK


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "AUTH_TOKEN": "tok_xyz",
        "PORT": "8080",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
    }


def test_returns_mask_result(sample_env):
    result = mask_env(sample_env, "prod.env")
    assert isinstance(result, MaskResult)


def test_filename_stored(sample_env):
    result = mask_env(sample_env, "prod.env")
    assert result.filename == "prod.env"


def test_non_sensitive_keys_unchanged(sample_env):
    result = mask_env(sample_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "8080"
    assert result.masked["DEBUG"] == "true"


def test_sensitive_keys_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_PASSWORD"] == MASK
    assert result.masked["API_KEY"] == MASK
    assert result.masked["AUTH_TOKEN"] == MASK
    assert result.masked["SECRET_KEY"] == MASK


def test_mask_count(sample_env):
    result = mask_env(sample_env)
    assert result.mask_count == 4


def test_masked_keys_sorted(sample_env):
    result = mask_env(sample_env)
    assert result.masked_keys == sorted(result.masked_keys)


def test_original_preserved(sample_env):
    result = mask_env(sample_env)
    assert result.original["DB_PASSWORD"] == "s3cr3t"
    assert result.original["API_KEY"] == "abc123"


def test_is_clean_when_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
    result = mask_env(env)
    assert result.is_clean
    assert result.mask_count == 0


def test_is_not_clean_when_sensitive(sample_env):
    result = mask_env(sample_env)
    assert not result.is_clean


def test_empty_env():
    result = mask_env({}, "empty.env")
    assert result.is_clean
    assert result.masked == {}
    assert result.masked_keys == []
