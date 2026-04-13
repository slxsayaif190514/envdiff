"""Tests for envdiff.parser module."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError


@pytest.fixture
def tmp_env(tmp_path):
    """Helper that writes a .env file and returns its path."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


def test_basic_key_value(tmp_env):
    path = tmp_env("APP_NAME=envdiff\nDEBUG=true\n")
    result = parse_env_file(path)
    assert result == {"APP_NAME": "envdiff", "DEBUG": "true"}


def test_double_quoted_value(tmp_env):
    path = tmp_env('DB_URL="postgres://localhost/mydb"\n')
    result = parse_env_file(path)
    assert result["DB_URL"] == "postgres://localhost/mydb"


def test_single_quoted_value(tmp_env):
    path = tmp_env("SECRET='my secret value'\n")
    result = parse_env_file(path)
    assert result["SECRET"] == "my secret value"


def test_empty_value_becomes_none(tmp_env):
    path = tmp_env("OPTIONAL_KEY=\n")
    result = parse_env_file(path)
    assert result["OPTIONAL_KEY"] is None


def test_comments_and_blank_lines_ignored(tmp_env):
    content = "# this is a comment\n\nAPP=foo\n# another comment\nBAR=baz\n"
    path = tmp_env(content)
    result = parse_env_file(path)
    assert result == {"APP": "foo", "BAR": "baz"}


def test_file_not_found():
    with pytest.raises(EnvParseError, match="File not found"):
        parse_env_file("/nonexistent/path/.env")


def test_invalid_line_raises_error(tmp_env):
    path = tmp_env("BADLINE\n")
    with pytest.raises(EnvParseError, match="Invalid syntax at line 1"):
        parse_env_file(path)


def test_empty_key_raises_error(tmp_env):
    path = tmp_env("=value\n")
    with pytest.raises(EnvParseError, match="Empty key at line 1"):
        parse_env_file(path)


def test_value_with_equals_sign(tmp_env):
    """Values that contain '=' should be preserved correctly."""
    path = tmp_env("TOKEN=abc=def=ghi\n")
    result = parse_env_file(path)
    assert result["TOKEN"] == "abc=def=ghi"
