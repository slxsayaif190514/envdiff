"""Tests for envdiff.differ_density."""
import pytest
from envdiff.differ_density import build_density, DensityEntry, DensityResult


@pytest.fixture
def sample_env():
    return {
        "EMPTY_KEY": "",
        "SHORT": "hi",
        "NORMAL": "some_value_here",
        "LONG_KEY": "x" * 64,
    }


def test_build_density_returns_result(sample_env):
    result = build_density(sample_env, filename="test.env")
    assert isinstance(result, DensityResult)


def test_filename_stored(sample_env):
    result = build_density(sample_env, filename="prod.env")
    assert result.filename == "prod.env"


def test_key_count_matches_env(sample_env):
    result = build_density(sample_env)
    assert result.key_count == len(sample_env)


def test_empty_key_detected(sample_env):
    result = build_density(sample_env)
    entry = result.get("EMPTY_KEY")
    assert entry is not None
    assert entry.is_empty is True
    assert entry.length == 0


def test_short_key_detected(sample_env):
    result = build_density(sample_env)
    entry = result.get("SHORT")
    assert entry is not None
    assert entry.is_short is True
    assert entry.is_empty is False


def test_long_key_detected(sample_env):
    result = build_density(sample_env)
    entry = result.get("LONG_KEY")
    assert entry is not None
    assert entry.is_long is True
    assert entry.length == 64


def test_normal_key_not_short_or_long(sample_env):
    result = build_density(sample_env)
    entry = result.get("NORMAL")
    assert entry is not None
    assert entry.is_short is False
    assert entry.is_long is False
    assert entry.is_empty is False


def test_empty_count(sample_env):
    result = build_density(sample_env)
    assert result.empty_count == 1


def test_short_count(sample_env):
    result = build_density(sample_env)
    assert result.short_count == 1


def test_long_count(sample_env):
    result = build_density(sample_env)
    assert result.long_count == 1


def test_average_length_empty_env():
    result = build_density({})
    assert result.average_length == 0.0


def test_average_length_computed():
    env = {"A": "ab", "B": "abcd"}
    result = build_density(env)
    assert result.average_length == pytest.approx(3.0)


def test_get_missing_key_returns_none(sample_env):
    result = build_density(sample_env)
    assert result.get("DOES_NOT_EXIST") is None


def test_entries_sorted_alphabetically():
    env = {"Z_KEY": "z", "A_KEY": "a", "M_KEY": "m"}
    result = build_density(env)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
