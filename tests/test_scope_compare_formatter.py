"""Tests for envdiff.scope_compare_formatter."""
import re
import pytest
from envdiff.differ_scope import build_scope_compare
from envdiff.scope_compare_formatter import format_scope_compare


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


@pytest.fixture()
def simple_result():
    env_a = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
    env_b = {"DB_HOST": "prod.db", "DB_PORT": "5432", "NEW_KEY": "x"}
    return build_scope_compare(
        env_a, env_b,
        scope_keys=["DB_HOST", "DB_PORT"],
        file_a="dev.env",
        file_b="prod.env",
        scope_name="database",
    )


def test_header_contains_scope_name(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "database" in out


def test_header_contains_filenames(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "dev.env" in out
    assert "prod.env" in out


def test_in_scope_section_shown(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "In-scope" in out


def test_out_of_scope_section_shown(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "Out-of-scope" in out


def test_mismatch_key_shown(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "DB_HOST" in out


def test_match_count_in_output(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "matches:" in out
    assert "1" in out


def test_mismatch_count_in_output(simple_result):
    out = _strip(format_scope_compare(simple_result))
    assert "mismatches:" in out
