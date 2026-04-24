"""Tests for envdiff.digester."""

from __future__ import annotations

import pytest

from envdiff.digester import (
    DigestEntry,
    DigestResult,
    _hash_value,
    _hash_file,
    digest_env,
    compare_digests,
)


SAMPLE: dict[str, str] = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_hash_value_is_deterministic():
    assert _hash_value("hello") == _hash_value("hello")


def test_hash_value_differs_for_different_inputs():
    assert _hash_value("hello") != _hash_value("world")


def test_hash_file_is_deterministic():
    assert _hash_file(SAMPLE) == _hash_file(SAMPLE)


def test_hash_file_differs_when_value_changes():
    modified = {**SAMPLE, "DB_PORT": "9999"}
    assert _hash_file(SAMPLE) != _hash_file(modified)


def test_digest_env_key_count():
    result = digest_env("dev.env", SAMPLE)
    assert result.key_count == 3


def test_digest_env_filename_stored():
    result = digest_env("dev.env", SAMPLE)
    assert result.filename == "dev.env"


def test_digest_env_file_hash_nonempty():
    result = digest_env("dev.env", SAMPLE)
    assert len(result.file_hash) == 64  # sha256 hex


def test_digest_env_entry_hash_matches_value():
    result = digest_env("dev.env", SAMPLE)
    assert result.entries["DB_HOST"].value_hash == _hash_value("localhost")


def test_digest_env_get_returns_entry():
    result = digest_env("dev.env", SAMPLE)
    entry = result.get("SECRET")
    assert isinstance(entry, DigestEntry)
    assert entry.raw_value == "abc"


def test_digest_env_get_missing_returns_none():
    result = digest_env("dev.env", SAMPLE)
    assert result.get("MISSING") is None


def test_compare_digests_identical_envs():
    a = digest_env("a.env", SAMPLE)
    b = digest_env("b.env", SAMPLE)
    assert compare_digests(a, b) == {}


def test_compare_digests_changed_value():
    a = digest_env("a.env", SAMPLE)
    b = digest_env("b.env", {**SAMPLE, "DB_PORT": "9999"})
    diffs = compare_digests(a, b)
    assert diffs.get("DB_PORT") == "changed"


def test_compare_digests_only_in_a():
    a = digest_env("a.env", SAMPLE)
    b = digest_env("b.env", {"DB_HOST": "localhost"})
    diffs = compare_digests(a, b)
    assert diffs.get("DB_PORT") == "only_in_a"
    assert diffs.get("SECRET") == "only_in_a"


def test_compare_digests_only_in_b():
    a = digest_env("a.env", {"DB_HOST": "localhost"})
    b = digest_env("b.env", SAMPLE)
    diffs = compare_digests(a, b)
    assert diffs.get("DB_PORT") == "only_in_b"


def test_compare_digests_no_false_positives_for_same_values():
    a = digest_env("a.env", {"KEY": "value"})
    b = digest_env("b.env", {"KEY": "value"})
    assert "KEY" not in compare_digests(a, b)
