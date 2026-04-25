"""Tests for differ_frequency module."""
import pytest
from envdiff.differ_frequency import analyze_frequency, FrequencyEntry, FrequencyResult


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "prod.db", "DB_PORT": "5432", "APP_ENV": "production"}
ENV_C = {"DB_HOST": "staging.db", "CACHE_URL": "redis://localhost"}


def test_result_is_frequency_result():
    result = analyze_frequency([ENV_A, ENV_B])
    assert isinstance(result, FrequencyResult)


def test_key_count_matches_unique_keys():
    result = analyze_frequency([ENV_A, ENV_B])
    expected_keys = {"DB_HOST", "DB_PORT", "SECRET", "APP_ENV"}
    assert result.key_count == len(expected_keys)


def test_universal_key_detected():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    assert "DB_HOST" in result.universal_keys


def test_rare_key_detected():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    # SECRET only in ENV_A (1/3 = 33%)
    assert "SECRET" in result.rare_keys


def test_ratio_correct():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    entry = result.get("DB_HOST")
    assert entry is not None
    assert entry.ratio == pytest.approx(1.0)


def test_sources_list_populated():
    result = analyze_frequency([ENV_A, ENV_B], filenames=["a.env", "b.env"])
    entry = result.get("DB_HOST")
    assert "a.env" in entry.sources
    assert "b.env" in entry.sources


def test_sources_partial():
    result = analyze_frequency([ENV_A, ENV_B], filenames=["a.env", "b.env"])
    entry = result.get("SECRET")
    assert entry.sources == ["a.env"]


def test_entries_sorted_alphabetically():
    result = analyze_frequency([ENV_A, ENV_B])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_get_returns_none_for_missing_key():
    result = analyze_frequency([ENV_A])
    assert result.get("NONEXISTENT") is None


def test_empty_envs_returns_empty_result():
    result = analyze_frequency([])
    assert result.key_count == 0
    assert result.universal_keys == []
    assert result.rare_keys == []


def test_mismatched_filenames_raises():
    with pytest.raises(ValueError, match="filenames length"):
        analyze_frequency([ENV_A, ENV_B], filenames=["only_one.env"])


def test_label_stored_in_result():
    result = analyze_frequency([ENV_A], label="custom-label")
    assert result.filename == "custom-label"


def test_is_universal_false_when_not_all():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    entry = result.get("SECRET")
    assert not entry.is_universal


def test_is_rare_false_when_majority_present():
    result = analyze_frequency([ENV_A, ENV_B, ENV_C])
    entry = result.get("DB_HOST")
    assert not entry.is_rare
