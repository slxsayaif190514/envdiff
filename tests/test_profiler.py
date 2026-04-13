"""Tests for envdiff.profiler and envdiff.profiler_formatter."""
from __future__ import annotations

import os
import pytest

from envdiff.profiler import profile_env_file
from envdiff.profiler_formatter import format_profile


@pytest.fixture()
def tmp_env(tmp_path):
    """Return a helper that writes an env file and gives back its path."""
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content)
        return str(p)
    return _write


def test_total_keys(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=qux\n")
    profile = profile_env_file(path)
    assert profile.total_keys == 2


def test_empty_value_detected(tmp_env):
    path = tmp_env("EMPTY=\nFOO=bar\n")
    profile = profile_env_file(path)
    assert "EMPTY" in profile.empty_values
    assert "FOO" not in profile.empty_values


def test_boolean_value_detected(tmp_env):
    path = tmp_env("DEBUG=true\nVERBOSE=false\nFOO=bar\n")
    profile = profile_env_file(path)
    assert "DEBUG" in profile.boolean_values
    assert "VERBOSE" in profile.boolean_values
    assert "FOO" not in profile.boolean_values


def test_numeric_value_detected(tmp_env):
    path = tmp_env("PORT=8080\nTIMEOUT=3.5\nNAME=app\n")
    profile = profile_env_file(path)
    assert "PORT" in profile.numeric_values
    assert "TIMEOUT" in profile.numeric_values
    assert "NAME" not in profile.numeric_values


def test_url_value_detected(tmp_env):
    path = tmp_env("API_URL=https://example.com\nDB=postgres://localhost\n")
    profile = profile_env_file(path)
    assert "API_URL" in profile.url_values
    # postgres:// is not http/https/ftp so should not appear
    assert "DB" not in profile.url_values


def test_long_value_detected(tmp_env):
    long_val = "x" * 101
    path = tmp_env(f"BIG={long_val}\nSMALL=ok\n")
    profile = profile_env_file(path)
    assert "BIG" in profile.long_values
    assert "SMALL" not in profile.long_values


def test_prefix_counting(tmp_env):
    path = tmp_env("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n")
    profile = profile_env_file(path)
    assert profile.prefixes.get("DB") == 2
    assert profile.prefixes.get("APP") == 1


def test_is_empty_flag(tmp_env):
    path = tmp_env("")
    profile = profile_env_file(path)
    assert profile.is_empty


def test_format_profile_contains_filename(tmp_env):
    path = tmp_env("FOO=bar\n")
    profile = profile_env_file(path)
    output = format_profile(profile, color=False)
    assert os.path.basename(path) in output or path in output


def test_format_profile_shows_totals(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=1\n")
    profile = profile_env_file(path)
    output = format_profile(profile, color=False)
    assert "2" in output


def test_format_empty_env(tmp_env):
    path = tmp_env("")
    profile = profile_env_file(path)
    output = format_profile(profile, color=False)
    assert "no keys" in output
