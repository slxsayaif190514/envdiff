"""Tests for envdiff.differ_radar."""
import pytest
from envdiff.differ_radar import (
    RadarAxis,
    RadarResult,
    build_radar,
    _score_completeness,
    _score_consistency,
    _score_security,
    _score_naming,
)


# ---------------------------------------------------------------------------
# RadarAxis
# ---------------------------------------------------------------------------

def test_radar_axis_delta_positive():
    ax = RadarAxis("completeness", score_a=0.5, score_b=0.8)
    assert ax.delta == pytest.approx(0.3, abs=1e-4)


def test_radar_axis_delta_negative():
    ax = RadarAxis("security", score_a=0.9, score_b=0.6)
    assert ax.delta == pytest.approx(-0.3, abs=1e-4)


# ---------------------------------------------------------------------------
# RadarResult
# ---------------------------------------------------------------------------

def test_radar_result_overall_empty():
    r = RadarResult(file_a="a.env", file_b="b.env")
    assert r.overall_a == 1.0
    assert r.overall_b == 1.0


def test_radar_result_overall_average():
    r = RadarResult(file_a="a.env", file_b="b.env", axes=[
        RadarAxis("x", 0.8, 0.6),
        RadarAxis("y", 0.4, 0.8),
    ])
    assert r.overall_a == pytest.approx(0.6, abs=1e-4)
    assert r.overall_b == pytest.approx(0.7, abs=1e-4)


def test_radar_result_get_existing():
    ax = RadarAxis("naming", 0.5, 0.5)
    r = RadarResult(file_a="a.env", file_b="b.env", axes=[ax])
    assert r.get("naming") is ax


def test_radar_result_get_missing():
    r = RadarResult(file_a="a.env", file_b="b.env")
    assert r.get("nonexistent") is None


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def test_completeness_identical_keys():
    env = {"A": "1", "B": "2"}
    sa, sb = _score_completeness(env, env)
    assert sa == 1.0 and sb == 1.0


def test_completeness_disjoint():
    sa, sb = _score_completeness({"A": "1"}, {"B": "2"})
    assert sa == pytest.approx(0.5, abs=1e-4)
    assert sb == pytest.approx(0.5, abs=1e-4)


def test_completeness_empty():
    sa, sb = _score_completeness({}, {})
    assert sa == 1.0 and sb == 1.0


def test_consistency_all_match():
    env = {"X": "hello"}
    ca, cb = _score_consistency(env, env)
    assert ca == 1.0 and cb == 1.0


def test_consistency_none_match():
    ca, cb = _score_consistency({"X": "a"}, {"X": "b"})
    assert ca == 0.0 and cb == 0.0


def test_security_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert _score_security(env) == 1.0


def test_security_exposed_secret():
    env = {"DB_PASSWORD": "hunter2"}
    assert _score_security(env) == 0.0


def test_security_redacted_secret():
    env = {"API_KEY": "***"}
    assert _score_security(env) == 1.0


def test_naming_all_upper():
    env = {"FOO": "1", "BAR": "2"}
    assert _score_naming(env) == 1.0


def test_naming_mixed_case():
    env = {"FOO": "1", "bar": "2"}
    assert _score_naming(env) == pytest.approx(0.5, abs=1e-4)


# ---------------------------------------------------------------------------
# build_radar integration
# ---------------------------------------------------------------------------

def test_build_radar_returns_five_axes():
    r = build_radar("a.env", {"KEY": "val"}, "b.env", {"KEY": "val"})
    assert len(r.axes) == 5


def test_build_radar_axis_names():
    r = build_radar("a.env", {}, "b.env", {})
    names = [ax.name for ax in r.axes]
    assert "completeness" in names
    assert "security" in names
    assert "naming" in names


def test_build_radar_files_stored():
    r = build_radar("prod.env", {}, "staging.env", {})
    assert r.file_a == "prod.env"
    assert r.file_b == "staging.env"
