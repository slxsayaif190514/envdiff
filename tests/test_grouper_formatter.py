"""Tests for envdiff.grouper_formatter."""

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.grouper import group_result
from envdiff.grouper_formatter import format_group_result


def _diff(key: str, diff_type: str) -> KeyDiff:
    return KeyDiff(key=key, value_a="a", value_b="b", diff_type=diff_type)


def _make_result(**kwargs) -> CompareResult:
    defaults = dict(missing_in_b=[], missing_in_a=[], mismatches=[], matches=[])
    defaults.update(kwargs)
    return CompareResult(**defaults)


def test_header_shows_group_count():
    cr = _make_result(matches=[_diff("DB_HOST", "match"), _diff("DB_PORT", "match")])
    gr = group_result(cr)
    out = format_group_result(gr)
    assert "1 groups" in out


def test_group_name_appears_in_output():
    cr = _make_result(missing_in_b=[_diff("AWS_KEY", "missing_in_b")])
    gr = group_result(cr)
    out = format_group_result(gr)
    assert "AWS_*" in out


def test_issues_label_shown_for_bad_group():
    cr = _make_result(mismatches=[_diff("DB_HOST", "mismatch"), _diff("DB_PORT", "mismatch")])
    gr = group_result(cr)
    out = format_group_result(gr)
    assert "issues" in out


def test_ok_label_shown_for_clean_group():
    cr = _make_result(matches=[_diff("APP_ENV", "match"), _diff("APP_NAME", "match")])
    gr = group_result(cr)
    out = format_group_result(gr, show_matches=True)
    assert "ok" in out


def test_matches_hidden_by_default():
    cr = _make_result(matches=[_diff("APP_ENV", "match"), _diff("APP_NAME", "match")])
    gr = group_result(cr)
    out = format_group_result(gr, show_matches=False)
    assert "APP_ENV" not in out


def test_matches_shown_when_flag_set():
    cr = _make_result(matches=[_diff("APP_ENV", "match"), _diff("APP_NAME", "match")])
    gr = group_result(cr)
    out = format_group_result(gr, show_matches=True)
    assert "APP_ENV" in out


def test_ungrouped_section_present_for_bare_keys():
    cr = _make_result(missing_in_b=[_diff("DEBUG", "missing_in_b")])
    gr = group_result(cr)
    out = format_group_result(gr)
    assert "ungrouped" in out
    assert "DEBUG" in out


def test_total_keys_in_header():
    cr = _make_result(
        missing_in_b=[_diff("DB_HOST", "missing_in_b")],
        matches=[_diff("APP_ENV", "match")],
    )
    gr = group_result(cr)
    out = format_group_result(gr)
    assert f"{gr.total_keys} total keys" in out
