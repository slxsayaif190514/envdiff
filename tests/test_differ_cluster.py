"""Tests for envdiff.differ_cluster."""
import pytest
from envdiff.differ_cluster import cluster_env, ClusterEntry, ClusterResult


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "REDIS_HOST": "localhost",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
        "CACHE_HOST": "localhost",
    }


def test_cluster_returns_result(sample_env):
    result = cluster_env(sample_env, filename="test.env")
    assert isinstance(result, ClusterResult)


def test_filename_stored(sample_env):
    result = cluster_env(sample_env, filename="my.env")
    assert result.filename == "my.env"


def test_total_keys_matches_env(sample_env):
    result = cluster_env(sample_env, filename="test.env")
    assert result.total_keys == len(sample_env)


def test_shared_cluster_detected(sample_env):
    result = cluster_env(sample_env, filename="test.env")
    shared = [c for c in result.clusters if len(c.keys) > 1]
    assert len(shared) == 1
    assert set(shared[0].keys) == {"DB_HOST", "REDIS_HOST", "CACHE_HOST"}
    assert shared[0].value == "localhost"


def test_singleton_count(sample_env):
    result = cluster_env(sample_env, filename="test.env")
    assert result.singleton_count == 2  # APP_ENV and LOG_LEVEL


def test_shared_count(sample_env):
    result = cluster_env(sample_env, filename="test.env")
    assert result.shared_count == 1


def test_empty_env_returns_empty_result():
    result = cluster_env({}, filename="empty.env")
    assert result.cluster_count == 0
    assert result.total_keys == 0
    assert result.singleton_count == 0
    assert result.shared_count == 0


def test_all_unique_values():
    env = {"A": "1", "B": "2", "C": "3"}
    result = cluster_env(env, filename="test.env")
    assert result.cluster_count == 3
    assert result.singleton_count == 3
    assert result.shared_count == 0


def test_all_same_value():
    env = {"A": "x", "B": "x", "C": "x"}
    result = cluster_env(env, filename="test.env")
    assert result.cluster_count == 1
    assert result.shared_count == 1
    assert result.singleton_count == 0
    assert sorted(result.clusters[0].keys) == ["A", "B", "C"]


def test_keys_within_cluster_are_sorted():
    env = {"Z_KEY": "same", "A_KEY": "same", "M_KEY": "same"}
    result = cluster_env(env, filename="test.env")
    assert result.clusters[0].keys == ["A_KEY", "M_KEY", "Z_KEY"]


def test_empty_string_value_clusters():
    env = {"EMPTY1": "", "EMPTY2": "", "SET": "value"}
    result = cluster_env(env, filename="test.env")
    shared = [c for c in result.clusters if len(c.keys) > 1]
    assert len(shared) == 1
    assert set(shared[0].keys) == {"EMPTY1", "EMPTY2"}
