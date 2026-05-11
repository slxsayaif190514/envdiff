"""Tests for coverage_formatter module."""
import pytest
from envdiff.differ_coverage import compute_coverage
from envdiff.coverage_formatter import format_coverage_result


def _strip(text: str) -> str:
    """Remove ANSI escape codes."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", text)


@pytest.fixture()
def simple_result():
    envs = {
        "dev.env": {"DB_HOST": "localhost", "DEBUG": "true"},
        "prod.env": {"DB_HOST": "prod-db"},
    }
    return compute_coverage(envs)


def test_header_contains_filenames(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "dev.env" in out
    assert "prod.env" in out


def test_key_count_shown(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "2" in out  # 2 unique keys


def test_universal_key_present(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "DB_HOST" in out


def test_orphan_key_present(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "DEBUG" in out


def test_missing_in_shown(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "missing in" in out
    assert "prod.env" in out


def test_universal_label_shown(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "universal" in out


def test_orphan_label_shown(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "orphan" in out


def test_no_color_mode(simple_result):
    colored = format_coverage_result(simple_result)
    plain = format_coverage_result(simple_result, no_color=True)
    assert "\033[" not in plain
    assert _strip(colored) == plain


def test_empty_result_shows_no_keys():
    result = compute_coverage({})
    out = _strip(format_coverage_result(result))
    assert "No keys found" in out


def test_average_coverage_shown(simple_result):
    out = _strip(format_coverage_result(simple_result))
    assert "Average coverage" in out
