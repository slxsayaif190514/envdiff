"""Tests for envdiff.differ_entropy."""

import pytest

from envdiff.differ_entropy import (
    EntropyEntry,
    EntropyResult,
    _shannon_entropy,
    _entropy_level,
    analyse_entropy,
)


# ---------------------------------------------------------------------------
# _shannon_entropy
# ---------------------------------------------------------------------------

def test_entropy_empty_string_is_zero():
    assert _shannon_entropy("") == 0.0


def test_entropy_single_char_is_zero():
    assert _shannon_entropy("aaaa") == pytest.approx(0.0, abs=1e-9)


def test_entropy_two_equal_chars_is_one():
    # "ab" repeated — perfectly balanced 2-symbol source → entropy = 1.0
    assert _shannon_entropy("abab") == pytest.approx(1.0, abs=1e-9)


def test_entropy_increases_with_diversity():
    low = _shannon_entropy("aaab")
    high = _shannon_entropy("abcdefgh")
    assert high > low


# ---------------------------------------------------------------------------
# _entropy_level
# ---------------------------------------------------------------------------

def test_level_empty_value_is_low():
    assert _entropy_level(4.0, 0) == "low"


def test_level_high_entropy_long_value():
    assert _entropy_level(3.8, 20) == "high"


def test_level_medium_entropy():
    assert _entropy_level(2.5, 8) == "medium"


def test_level_low_entropy():
    assert _entropy_level(1.0, 6) == "low"


# ---------------------------------------------------------------------------
# analyse_entropy
# ---------------------------------------------------------------------------

SIMPLE_ENV = {
    "DB_HOST": "localhost",
    "SECRET_KEY": "xK9#mP2$qL7!nR4@wZ",
    "PORT": "8080",
    "EMPTY": "",
}


@pytest.fixture
def result():
    return analyse_entropy("test.env", SIMPLE_ENV)


def test_result_filename(result):
    assert result.filename == "test.env"


def test_result_key_count(result):
    assert result.key_count == len(SIMPLE_ENV)


def test_entries_sorted_alphabetically(result):
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_empty_value_is_low_entropy(result):
    entry = next(e for e in result.entries if e.key == "EMPTY")
    assert entry.entropy == 0.0
    assert entry.level == "low"


def test_secret_key_is_high_entropy(result):
    entry = next(e for e in result.entries if e.key == "SECRET_KEY")
    assert entry.level == "high"


def test_average_entropy_is_positive(result):
    assert result.average_entropy > 0.0


def test_high_entropy_keys_list(result):
    assert "SECRET_KEY" in result.high_entropy_keys


def test_low_entropy_keys_list(result):
    assert "EMPTY" in result.low_entropy_keys


def test_empty_env_returns_zero_average():
    r = analyse_entropy("empty.env", {})
    assert r.average_entropy == 0.0
    assert r.key_count == 0
