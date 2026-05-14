"""Tests for envdiff.lineage_formatter."""

import re
from envdiff.differ_lineage import build_lineage
from envdiff.lineage_formatter import format_lineage_result


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def _make(snaps, labels=None):
    return build_lineage(snaps, labels=labels)


def test_header_contains_key_count():
    result = _make([{"A": "1", "B": "2"}, {"A": "1"}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "2 keys" in out


def test_header_contains_snapshot_count():
    result = _make([{"A": "v"}, {"A": "v"}], labels=["dev", "prod"])
    out = _strip(format_lineage_result(result))
    assert "2 snapshots" in out


def test_snapshot_labels_listed():
    result = _make([{"A": "v"}], labels=["alpha"])
    out = _strip(format_lineage_result(result))
    assert "alpha" in out


def test_key_appears_in_output():
    result = _make([{"MY_KEY": "hello"}], labels=["s1"])
    out = _strip(format_lineage_result(result))
    assert "MY_KEY" in out


def test_stable_label_shown():
    result = _make([{"A": "v"}, {"A": "v"}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "stable" in out


def test_unstable_label_shown():
    result = _make([{"A": "v1"}, {"A": "v2"}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "unstable" in out


def test_all_stable_message():
    result = _make([{"A": "v"}, {"A": "v"}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "All keys are stable" in out


def test_unstable_summary_message():
    result = _make([{"A": "v1"}, {"A": "v2"}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "unstable key" in out


def test_no_color_flag_strips_escapes():
    result = _make([{"A": "v"}], labels=["s1"])
    out = format_lineage_result(result, no_color=True)
    assert "\033[" not in out


def test_absent_value_shown():
    result = _make([{"A": "v"}, {}], labels=["s1", "s2"])
    out = _strip(format_lineage_result(result))
    assert "absent" in out
