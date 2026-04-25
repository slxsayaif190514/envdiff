"""Tests for frequency_formatter module."""
import re
from envdiff.differ_frequency import analyze_frequency
from envdiff.frequency_formatter import format_frequency_result


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "prod.db", "DB_PORT": "5432", "APP_ENV": "production"}
ENV_C = {"DB_HOST": "staging.db", "CACHE_URL": "redis://localhost"}


def test_header_contains_label():
    result = analyze_frequency([ENV_A, ENV_B], label="test-label")
    output = _strip(format_frequency_result(result))
    assert "test-label" in output


def test_header_contains_key_count():
    result = analyze_frequency([ENV_A, ENV_B])
    output = _strip(format_frequency_result(result))
    assert str(result.key_count) in output


def test_each_key_appears_in_output():
    result = analyze_frequency([ENV_A, ENV_B])
    output = _strip(format_frequency_result(result))
    for entry in result.entries:
        assert entry.key in output


def test_percentage_shown():
    result = analyze_frequency([ENV_A, ENV_B])
    output = _strip(format_frequency_result(result))
    assert "%" in output


def test_summary_line_present():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    output = _strip(format_frequency_result(result))
    assert "Universal:" in output
    assert "Rare" in output


def test_empty_result_shows_no_keys_message():
    result = analyze_frequency([])
    output = _strip(format_frequency_result(result))
    assert "No keys found" in output


def test_color_false_no_escape_codes():
    result = analyze_frequency([ENV_A, ENV_B])
    output = format_frequency_result(result, color=False)
    assert "\033[" not in output


def test_sources_shown_in_output():
    result = analyze_frequency([ENV_A, ENV_B], filenames=["alpha.env", "beta.env"])
    output = _strip(format_frequency_result(result))
    assert "alpha.env" in output
    assert "beta.env" in output
