"""Tests for envdiff.cluster_formatter."""
import pytest
from envdiff.differ_cluster import cluster_env, ClusterResult
from envdiff.cluster_formatter import format_cluster_result


def _strip(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


@pytest.fixture
def shared_result():
    env = {
        "DB_HOST": "localhost",
        "REDIS_HOST": "localhost",
        "APP_ENV": "production",
    }
    return cluster_env(env, filename="app.env")


@pytest.fixture
def unique_result():
    env = {"A": "1", "B": "2"}
    return cluster_env(env, filename="unique.env")


def test_header_contains_filename(shared_result):
    out = _strip(format_cluster_result(shared_result))
    assert "app.env" in out


def test_cluster_count_shown(shared_result):
    out = _strip(format_cluster_result(shared_result))
    assert "2 clusters" in out


def test_shared_count_shown(shared_result):
    out = _strip(format_cluster_result(shared_result))
    assert "1 shared" in out


def test_shared_keys_appear(shared_result):
    out = _strip(format_cluster_result(shared_result))
    assert "DB_HOST" in out
    assert "REDIS_HOST" in out


def test_unique_label_shown(unique_result):
    out = _strip(format_cluster_result(unique_result))
    assert "[unique]" in out


def test_shared_label_shown(shared_result):
    out = _strip(format_cluster_result(shared_result))
    assert "shared by 2 keys" in out


def test_show_values_includes_value(shared_result):
    out = _strip(format_cluster_result(shared_result, show_values=True))
    assert "localhost" in out


def test_hide_values_by_default(shared_result):
    out = _strip(format_cluster_result(shared_result, show_values=False))
    assert "localhost" not in out
