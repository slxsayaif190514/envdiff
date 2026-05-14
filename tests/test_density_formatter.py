"""Tests for envdiff.density_formatter."""
import re
import pytest
from envdiff.differ_density import build_density
from envdiff.density_formatter import format_density_result


def _strip(text: str) -> str:
    """Remove ANSI escape codes."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


@pytest.fixture
def simple_result():
    env = {
        "EMPTY": "",
        "SHORT": "hi",
        "NORMAL": "a_normal_value",
        "LONG": "x" * 64,
    }
    return build_density(env, filename="sample.env")


def test_header_contains_filename(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "sample.env" in out


def test_key_count_shown(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "Keys: 4" in out


def test_empty_count_shown(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "Empty: 1" in out


def test_short_count_shown(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "Short: 1" in out


def test_long_count_shown(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "Long: 1" in out


def test_each_key_appears(simple_result):
    out = _strip(format_density_result(simple_result))
    for key in ("EMPTY", "SHORT", "NORMAL", "LONG"):
        assert key in out


def test_empty_env_shows_no_keys_message():
    result = build_density({}, filename="empty.env")
    out = _strip(format_density_result(result))
    assert "no keys" in out


def test_average_length_in_output(simple_result):
    out = _strip(format_density_result(simple_result))
    assert "Avg length:" in out
