import pytest
from envdiff.differ_catalog import build_catalog, CatalogEntry, CatalogResult


@pytest.fixture
default_envs = None


@pytest.fixture
def three_envs():
    a = {"DB_HOST": "localhost", "APP_PORT": "8080", "SECRET": "abc"}
    b = {"DB_HOST": "prod-db", "APP_PORT": "8080"}
    c = {"DB_HOST": "staging-db", "EXTRA_KEY": "only-here"}
    return [a, b, c], ["a.env", "b.env", "c.env"]


def test_result_type(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    assert isinstance(result, CatalogResult)


def test_filenames_stored(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    assert result.filenames == names


def test_key_count_is_unique_keys(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    all_keys = set()
    for e in envs:
        all_keys.update(e.keys())
    assert result.key_count == len(all_keys)


def test_universal_key_present_in_all(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    universal = [e.key for e in result.universal_keys]
    assert "DB_HOST" in universal


def test_partial_key_not_in_all(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    partial = [e.key for e in result.partial_keys]
    assert "SECRET" in partial
    assert "EXTRA_KEY" in partial


def test_occurrence_count_correct(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    entry = result.get("APP_PORT")
    assert entry is not None
    assert entry.occurrence_count == 2


def test_sources_has_none_for_absent_file(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    entry = result.get("EXTRA_KEY")
    assert entry is not None
    assert entry.sources["a.env"] is None
    assert entry.sources["b.env"] is None
    assert entry.sources["c.env"] == "only-here"


def test_get_returns_none_for_missing_key(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    assert result.get("NONEXISTENT") is None


def test_entries_sorted_alphabetically(three_envs):
    envs, names = three_envs
    result = build_catalog(envs, names)
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)


def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        build_catalog([{"A": "1"}], ["a.env", "b.env"])


def test_empty_input_returns_empty_result():
    result = build_catalog([], [])
    assert result.key_count == 0
    assert result.filenames == []
