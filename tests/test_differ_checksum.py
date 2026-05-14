"""Tests for differ_checksum and checksum_formatter."""
import pytest

from envdiff.differ_checksum import (
    ChecksumEntry,
    ChecksumResult,
    _checksum_env,
    build_checksum_result,
)
from envdiff.checksum_formatter import format_checksum_result


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_C = {"DB_HOST": "remotehost", "DB_PORT": "5432", "SECRET": "xyz"}


def test_checksum_deterministic():
    assert _checksum_env(ENV_A) == _checksum_env(ENV_A)


def test_checksum_differs_for_different_envs():
    assert _checksum_env(ENV_A) != _checksum_env(ENV_C)


def test_checksum_same_for_identical_envs():
    assert _checksum_env(ENV_A) == _checksum_env(ENV_B)


def test_checksum_order_independent():
    env1 = {"A": "1", "B": "2"}
    env2 = {"B": "2", "A": "1"}
    assert _checksum_env(env1) == _checksum_env(env2)


def test_build_checksum_result_file_count():
    result = build_checksum_result([ENV_A, ENV_C], [".env.dev", ".env.prod"])
    assert result.file_count == 2


def test_build_checksum_result_key_count():
    result = build_checksum_result([ENV_A], [".env"])
    assert result.entries[0].key_count == 3


def test_build_checksum_result_all_match_true():
    result = build_checksum_result([ENV_A, ENV_B], ["a", "b"])
    assert result.all_match is True


def test_build_checksum_result_all_match_false():
    result = build_checksum_result([ENV_A, ENV_C], ["a", "c"])
    assert result.all_match is False


def test_build_checksum_single_file_always_matches():
    result = build_checksum_result([ENV_A], ["only"])
    assert result.all_match is True


def test_build_checksum_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        build_checksum_result([ENV_A, ENV_B], ["only_one"])


def test_get_entry_by_filename():
    result = build_checksum_result([ENV_A], [".env"])
    entry = result.get(".env")
    assert entry is not None
    assert entry.filename == ".env"


def test_get_entry_missing_returns_none():
    result = build_checksum_result([ENV_A], [".env"])
    assert result.get(".env.missing") is None


def _strip(s: str) -> str:
    import re
    return re.sub(r"\033\[[\d;]*m", "", s)


def test_formatter_shows_file_count():
    result = build_checksum_result([ENV_A, ENV_C], ["a", "c"])
    out = _strip(format_checksum_result(result))
    assert "2 file" in out


def test_formatter_match_message():
    result = build_checksum_result([ENV_A, ENV_B], ["a", "b"])
    out = _strip(format_checksum_result(result))
    assert "match" in out.lower()


def test_formatter_differ_message():
    result = build_checksum_result([ENV_A, ENV_C], ["a", "c"])
    out = _strip(format_checksum_result(result))
    assert "differ" in out.lower()


def test_formatter_filenames_shown():
    result = build_checksum_result([ENV_A], [".env.staging"])
    out = _strip(format_checksum_result(result))
    assert ".env.staging" in out
