"""Tests for envdiff.radar_formatter."""
import pytest
from envdiff.differ_radar import RadarAxis, RadarResult, build_radar
from envdiff.radar_formatter import format_radar_result


def _strip(s: str) -> str:
    """Remove ANSI escape codes for plain-text assertions."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


@pytest.fixture()
def simple_result() -> RadarResult:
    return build_radar(
        "prod.env",
        {"DB_HOST": "localhost", "DB_PASSWORD": "secret", "PORT": "5432"},
        "staging.env",
        {"DB_HOST": "staging-db", "DB_PASSWORD": "", "PORT": "5432"},
    )


def test_header_contains_filenames(simple_result):
    out = _strip(format_radar_result(simple_result))
    assert "prod.env" in out
    assert "staging.env" in out


def test_all_axes_present(simple_result):
    out = _strip(format_radar_result(simple_result))
    for axis in ("completeness", "consistency", "security", "type_alignment", "naming"):
        assert axis in out


def test_overall_row_present(simple_result):
    out = _strip(format_radar_result(simple_result))
    assert "Overall" in out


def test_no_color_flag_strips_ansi(simple_result):
    colored = format_radar_result(simple_result)
    plain = format_radar_result(simple_result, no_color=True)
    assert "\033[" not in plain
    assert len(plain) < len(colored)


def test_score_values_appear(simple_result):
    out = _strip(format_radar_result(simple_result))
    # scores are formatted as x.xx floats
    import re
    scores = re.findall(r"\d\.\d{2}", out)
    assert len(scores) >= 5  # at least one per axis


def test_delta_column_present(simple_result):
    out = _strip(format_radar_result(simple_result))
    assert "Delta" in out


def test_bar_column_present(simple_result):
    out = _strip(format_radar_result(simple_result, no_color=True))
    assert "[" in out and "]" in out


def test_empty_envs_does_not_crash():
    r = build_radar("a.env", {}, "b.env", {})
    out = _strip(format_radar_result(r))
    assert "Overall" in out
