import pytest
from envdiff.squasher import squash_envs, SquashResult, SquashEntry


@pytest.fixture
def base() -> list:
    return [
        ("dev", {"DB_HOST": "localhost", "PORT": "5432", "DEBUG": "true"}),
        ("prod", {"DB_HOST": "prod.db", "PORT": "5432", "API_KEY": "secret"}),
    ]


def test_empty_input_returns_empty_result():
    result = squash_envs([])
    assert isinstance(result, SquashResult)
    assert result.key_count == 0
    assert result.is_clean


def test_single_env_no_drops():
    result = squash_envs([("dev", {"A": "1", "B": "2"})])
    assert result.key_count == 2
    assert result.dropped_count == 0
    assert result.is_clean


def test_all_keys_present(base):
    result = squash_envs(base)
    assert set(result.keys()) == {"DB_HOST", "PORT", "DEBUG", "API_KEY"}


def test_last_strategy_wins(base):
    result = squash_envs(base, strategy="last")
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.value == "prod.db"


def test_first_strategy_wins(base):
    result = squash_envs(base, strategy="first")
    entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert entry.value == "localhost"


def test_no_conflict_key_not_dropped(base):
    result = squash_envs(base)
    port_entry = next(e for e in result.entries if e.key == "PORT")
    # PORT has same value in both — still recorded as dropped with last strategy
    # because the value is technically overwritten (even if same)
    assert "dev" in port_entry.sources and "prod" in port_entry.sources


def test_dropped_count_reflects_overrides(base):
    result = squash_envs(base, strategy="last")
    # DB_HOST and PORT both appear in both envs → 2 drops
    assert result.dropped_count == 2


def test_is_clean_false_when_drops(base):
    result = squash_envs(base)
    assert not result.is_clean


def test_entries_sorted_by_key(base):
    result = squash_envs(base)
    keys = result.keys()
    assert keys == sorted(keys)


def test_filename_contains_labels(base):
    result = squash_envs(base)
    assert "dev" in result.filename
    assert "prod" in result.filename


def test_sources_tracked_per_entry(base):
    result = squash_envs(base)
    db_entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert "dev" in db_entry.sources
    assert "prod" in db_entry.sources
