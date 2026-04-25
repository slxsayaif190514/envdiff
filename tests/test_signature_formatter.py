"""Tests for envdiff.signature_formatter"""
import re
import pytest
from envdiff.differ_signature import sign_env
from envdiff.signature_formatter import format_signature, format_signature_diff


def _strip(s: str) -> str:
    """Strip ANSI escape codes."""
    return re.sub(r"\033\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# format_signature
# ---------------------------------------------------------------------------

def test_format_signature_contains_filename():
    sig = sign_env("dev.env", {"FOO": "bar"})
    out = _strip(format_signature(sig))
    assert "dev.env" in out


def test_format_signature_shows_key_count():
    sig = sign_env("dev.env", {"A": "1", "B": "2"})
    out = _strip(format_signature(sig))
    assert "2" in out


def test_format_signature_shows_file_hash():
    sig = sign_env("dev.env", {"A": "1"})
    out = _strip(format_signature(sig))
    assert sig.file_hash in out


def test_format_signature_lists_keys():
    sig = sign_env("dev.env", {"DATABASE_URL": "postgres://", "PORT": "5432"})
    out = _strip(format_signature(sig))
    assert "DATABASE_URL" in out
    assert "PORT" in out


def test_format_signature_shows_value_type():
    sig = sign_env("dev.env", {"PORT": "8080"})
    out = _strip(format_signature(sig))
    assert "int" in out


def test_format_signature_empty_env():
    sig = sign_env("empty.env", {})
    out = _strip(format_signature(sig))
    assert "no keys" in out


# ---------------------------------------------------------------------------
# format_signature_diff
# ---------------------------------------------------------------------------

def test_format_signature_diff_identical():
    sig_a = sign_env("a.env", {"PORT": "8080"})
    sig_b = sign_env("b.env", {"PORT": "9090"})  # same structure
    out = _strip(format_signature_diff(sig_a, sig_b))
    assert "IDENTICAL" in out


def test_format_signature_diff_differs():
    sig_a = sign_env("a.env", {"PORT": "8080"})
    sig_b = sign_env("b.env", {"PORT": "not-a-number"})
    out = _strip(format_signature_diff(sig_a, sig_b))
    assert "DIFFERS" in out


def test_format_signature_diff_shows_filenames():
    sig_a = sign_env("a.env", {})
    sig_b = sign_env("b.env", {})
    out = _strip(format_signature_diff(sig_a, sig_b))
    assert "a.env" in out
    assert "b.env" in out


def test_format_signature_diff_shows_added_key():
    sig_a = sign_env("a.env", {})
    sig_b = sign_env("b.env", {"NEW_KEY": "value"})
    out = _strip(format_signature_diff(sig_a, sig_b))
    assert "NEW_KEY" in out


def test_format_signature_diff_shows_type_change():
    sig_a = sign_env("a.env", {"TIMEOUT": "30"})
    sig_b = sign_env("b.env", {"TIMEOUT": "thirty"})
    out = _strip(format_signature_diff(sig_a, sig_b))
    assert "TIMEOUT" in out
    assert "int" in out
    assert "string" in out
