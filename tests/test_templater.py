import pytest
from envdiff.templater import (
    TemplateEntry,
    TemplateResult,
    _make_placeholder,
    build_template,
)


# ---------------------------------------------------------------------------
# _make_placeholder
# ---------------------------------------------------------------------------

def test_placeholder_empty_value():
    assert _make_placeholder("SOME_KEY", "") == ""


def test_placeholder_secret_key():
    assert _make_placeholder("DB_PASSWORD", "hunter2") == "<secret>"


def test_placeholder_token():
    assert _make_placeholder("API_TOKEN", "abc123") == "<secret>"


def test_placeholder_url():
    assert _make_placeholder("DATABASE_URL", "postgres://localhost/db") == "<url>"


def test_placeholder_port():
    assert _make_placeholder("APP_PORT", "8080") == "<port>"


def test_placeholder_bool():
    assert _make_placeholder("DEBUG", "true") == "<bool>"
    assert _make_placeholder("ENABLED", "false") == "<bool>"


def test_placeholder_int():
    assert _make_placeholder("MAX_RETRIES", "5") == "<int>"


def test_placeholder_float():
    assert _make_placeholder("THRESHOLD", "0.95") == "<float>"


def test_placeholder_generic_string():
    assert _make_placeholder("APP_NAME", "myapp") == "<value>"


# ---------------------------------------------------------------------------
# build_template
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_envs():
    return {
        ".env.dev": {"APP_NAME": "dev", "DB_PASSWORD": "secret", "PORT": "3000"},
        ".env.prod": {"APP_NAME": "prod", "DB_PASSWORD": "topsecret", "LOG_LEVEL": "info"},
    }


def test_build_template_key_count(two_envs):
    result = build_template(two_envs)
    # APP_NAME, DB_PASSWORD, PORT, LOG_LEVEL
    assert result.key_count == 4


def test_build_template_source_files(two_envs):
    result = build_template(two_envs)
    assert set(result.source_files) == {".env.dev", ".env.prod"}


def test_build_template_no_duplicate_keys(two_envs):
    result = build_template(two_envs)
    keys = [e.key for e in result.entries]
    assert len(keys) == len(set(keys))


def test_build_template_secret_placeholder(two_envs):
    result = build_template(two_envs)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert entry.placeholder == "<secret>"


def test_build_template_comment_included(two_envs):
    result = build_template(two_envs, include_comments=True)
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.comment is not None
    assert ".env.dev" in entry.comment


def test_build_template_comment_suppressed(two_envs):
    result = build_template(two_envs, include_comments=False)
    for entry in result.entries:
        assert entry.comment is None


def test_to_lines_sorted(two_envs):
    result = build_template(two_envs, include_comments=False)
    lines = result.to_lines()
    keys_in_output = [line.split("=")[0] for line in lines if "=" in line]
    assert keys_in_output == sorted(keys_in_output)


def test_to_lines_with_comments(two_envs):
    result = build_template(two_envs, include_comments=True)
    lines = result.to_lines()
    comment_lines = [l for l in lines if l.startswith("#")]
    assert len(comment_lines) == result.key_count


def test_build_template_empty_env():
    result = build_template({})
    assert result.key_count == 0
    assert result.to_lines() == []
