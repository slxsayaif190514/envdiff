import pytest
from envdiff.deduplicator import DedupeEntry, DedupeResult, deduplicate_env


@pytest.fixture
def two_sources():
    a = {"DB_HOST": "localhost", "APP_PORT": "8000", "SHARED": "from_a"}
    b = {"DB_HOST": "prod-db", "SHARED": "from_b", "NEW_KEY": "hello"}
    return [("env_a", a), ("env_b", b)]


def test_clean_when_no_duplicates():
    result = deduplicate_env([("only", {"FOO": "1", "BAR": "2"})])
    assert result.is_clean
    assert result.dedupe_count == 0
    assert result.clean_env == {"FOO": "1", "BAR": "2"}


def test_first_strategy_keeps_first_value(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    assert result.clean_env["DB_HOST"] == "localhost"
    assert result.clean_env["SHARED"] == "from_a"


def test_last_strategy_keeps_last_value(two_sources):
    result = deduplicate_env(two_sources, strategy="last")
    assert result.clean_env["DB_HOST"] == "prod-db"
    assert result.clean_env["SHARED"] == "from_b"


def test_unique_keys_always_present(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    assert "APP_PORT" in result.clean_env
    assert "NEW_KEY" in result.clean_env


def test_affected_keys_only_duplicated(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    assert set(result.affected_keys) == {"DB_HOST", "SHARED"}


def test_dedupe_count_equals_dropped_occurrences(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    # DB_HOST and SHARED each have 1 dropped occurrence
    assert result.dedupe_count == 2


def test_entries_sorted_alphabetically(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_entry_dropped_contains_loser(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    db_entry = next(e for e in result.entries if e.key == "DB_HOST")
    dropped_sources = [s for s, _ in db_entry.duplicates]
    assert "env_b" in dropped_sources


def test_entry_kept_source_first_strategy(two_sources):
    result = deduplicate_env(two_sources, strategy="first")
    db_entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert db_entry.kept_source == "env_a"


def test_entry_kept_source_last_strategy(two_sources):
    result = deduplicate_env(two_sources, strategy="last")
    db_entry = next(e for e in result.entries if e.key == "DB_HOST")
    assert db_entry.kept_source == "env_b"


def test_label_used_as_filename():
    result = deduplicate_env([("x", {"A": "1"})], label="my-label")
    assert result.filename == "my-label"


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate_env([("x", {"A": "1"})], strategy="random")


def test_three_sources_last_wins():
    sources = [
        ("dev", {"KEY": "dev_val"}),
        ("staging", {"KEY": "staging_val"}),
        ("prod", {"KEY": "prod_val"}),
    ]
    result = deduplicate_env(sources, strategy="last")
    assert result.clean_env["KEY"] == "prod_val"
    assert result.dedupe_count == 2
