"""Tests for envdiff.symmetry_formatter."""
import re
from envdiff.differ_symmetry import compute_symmetry
from envdiff.symmetry_formatter import format_symmetry_result


def _strip(text: str) -> str:
    """Remove ANSI escape codes."""
    return re.sub(r"\033\[[0-9;]*m", "", text)


def test_header_contains_filenames():
    result = compute_symmetry({}, {}, file_a="a.env", file_b="b.env")
    out = _strip(format_symmetry_result(result))
    assert "a.env" in out
    assert "b.env" in out


def test_symmetric_shows_pass_message():
    result = compute_symmetry({"A": "1"}, {"A": "1"})
    out = _strip(format_symmetry_result(result))
    assert "fully symmetric" in out


def test_asymmetric_shows_fail_message():
    result = compute_symmetry({"A": "1"}, {"B": "2"})
    out = _strip(format_symmetry_result(result))
    assert "not fully symmetric" in out


def test_exclusive_a_keys_shown():
    result = compute_symmetry({"ONLY_A": "x"}, {"OTHER": "y"}, file_a="a", file_b="b")
    out = _strip(format_symmetry_result(result))
    assert "ONLY_A" in out


def test_exclusive_b_keys_shown():
    result = compute_symmetry({"OTHER": "y"}, {"ONLY_B": "z"}, file_a="a", file_b="b")
    out = _strip(format_symmetry_result(result))
    assert "ONLY_B" in out


def test_symmetry_ratio_percentage_shown():
    result = compute_symmetry({"A": "1", "B": "2"}, {"A": "1"})
    out = _strip(format_symmetry_result(result))
    # 1 shared out of 2 unique = 50%
    assert "50.0%" in out


def test_no_color_flag_removes_ansi():
    result = compute_symmetry({"A": "1"}, {"A": "1"})
    out = format_symmetry_result(result, color=False)
    assert "\033[" not in out


def test_total_keys_count_shown():
    result = compute_symmetry({"A": "1", "B": "2"}, {"B": "2", "C": "3"})
    out = _strip(format_symmetry_result(result))
    assert "3" in out  # 3 unique keys total
