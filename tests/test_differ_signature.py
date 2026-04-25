"""Tests for envdiff.differ_signature"""
import pytest
from envdiff.differ_signature import sign_env, _value_type, _short_hash, SignatureEntry


# ---------------------------------------------------------------------------
# _value_type
# ---------------------------------------------------------------------------

def test_value_type_empty():
    assert _value_type("") == "empty"


def test_value_type_bool_true():
    assert _value_type("true") == "bool"
    assert _value_type("True") == "bool"
    assert _value_type("yes") == "bool"


def test_value_type_int():
    assert _value_type("42") == "int"
    assert _value_type("-1") == "int"


def test_value_type_float():
    assert _value_type("3.14") == "float"


def test_value_type_url():
    assert _value_type("https://example.com") == "url"
    assert _value_type("http://localhost:8080") == "url"


def test_value_type_path():
    assert _value_type("/etc/ssl/certs") == "path"
    assert _value_type("./config") == "path"


def test_value_type_string():
    assert _value_type("hello world") == "string"
    assert _value_type("abc123xyz") == "string"


# ---------------------------------------------------------------------------
# _short_hash
# ---------------------------------------------------------------------------

def test_short_hash_length():
    assert len(_short_hash("anything")) == 8


def test_short_hash_deterministic():
    assert _short_hash("foo") == _short_hash("foo")


def test_short_hash_different_inputs():
    assert _short_hash("foo") != _short_hash("bar")


# ---------------------------------------------------------------------------
# sign_env
# ---------------------------------------------------------------------------

def test_sign_env_key_count():
    env = {"A": "1", "B": "hello", "C": ""}
    result = sign_env("test.env", env)
    assert result.key_count == 3


def test_sign_env_filename_stored():
    result = sign_env("prod.env", {})
    assert result.filename == "prod.env"


def test_sign_env_entries_sorted():
    env = {"Z": "1", "A": "2", "M": "3"}
    result = sign_env("x.env", env)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_sign_env_correct_types():
    env = {"PORT": "8080", "DEBUG": "true", "URL": "https://x.com"}
    result = sign_env("x.env", env)
    types = {e.key: e.value_type for e in result.entries}
    assert types["PORT"] == "int"
    assert types["DEBUG"] == "bool"
    assert types["URL"] == "url"


def test_sign_env_file_hash_changes_when_structure_changes():
    env_a = {"PORT": "8080"}
    env_b = {"PORT": "hello"}  # int -> string
    r_a = sign_env("a.env", env_a)
    r_b = sign_env("b.env", env_b)
    assert r_a.file_hash != r_b.file_hash


def test_sign_env_file_hash_stable_when_structure_same():
    env_a = {"PORT": "8080"}
    env_b = {"PORT": "9999"}  # both int, same structure
    r_a = sign_env("a.env", env_a)
    r_b = sign_env("b.env", env_b)
    assert r_a.file_hash == r_b.file_hash


def test_sign_env_get_existing_key():
    env = {"FOO": "bar"}
    result = sign_env("x.env", env)
    entry = result.get("FOO")
    assert entry is not None
    assert entry.key == "FOO"


def test_sign_env_get_missing_key():
    result = sign_env("x.env", {})
    assert result.get("MISSING") is None
