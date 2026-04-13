"""Tests for envdiff.merger_formatter."""

from envdiff.merger import MergeConflict, MergeResult
from envdiff.merger_formatter import format_merge_result


def _result_no_conflicts():
    return MergeResult(
        merged={"A": "1", "B": "2"},
        conflicts=[],
        sources=["dev.env", "prod.env"],
    )


def _result_with_conflicts():
    return MergeResult(
        merged={"HOST": "localhost", "PORT": "5432"},
        conflicts=[
            MergeConflict(
                key="HOST",
                values={"dev.env": "localhost", "prod.env": "remotehost"},
            )
        ],
        sources=["dev.env", "prod.env"],
    )


def test_no_conflict_message(capsys):
    output = format_merge_result(_result_no_conflicts(), no_color=True)
    assert "No conflicts found" in output


def test_sources_listed():
    output = format_merge_result(_result_no_conflicts(), no_color=True)
    assert "dev.env" in output
    assert "prod.env" in output


def test_total_key_count():
    output = format_merge_result(_result_no_conflicts(), no_color=True)
    assert "Total keys: 2" in output


def test_conflict_key_shown():
    output = format_merge_result(_result_with_conflicts(), no_color=True)
    assert "HOST" in output


def test_conflict_values_shown():
    output = format_merge_result(_result_with_conflicts(), no_color=True)
    assert "localhost" in output
    assert "remotehost" in output


def test_conflict_count_shown():
    output = format_merge_result(_result_with_conflicts(), no_color=True)
    assert "1 conflict" in output


def test_no_color_flag_removes_ansi():
    output = format_merge_result(_result_with_conflicts(), no_color=True)
    assert "\x1b[" not in output
