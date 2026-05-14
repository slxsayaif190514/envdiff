"""Tests for envdiff.differ_scope."""
import pytest
from envdiff.differ_scope import build_scope_compare, ScopeCompareEntry, ScopeCompareResult


@pytest.fixture()
def env_a():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev", "SECRET": "abc"}


@pytest.fixture()
def env_b():
    return {"DB_HOST": "prod.db", "DB_PORT": "5432", "APP_ENV": "prod", "NEW_KEY": "x"}


def test_result_type(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["DB_HOST", "DB_PORT"])
    assert isinstance(r, ScopeCompareResult)


def test_all_keys_present(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["DB_HOST"])
    keys = {e.key for e in r.entries}
    assert keys == set(env_a) | set(env_b)


def test_in_scope_keys_flagged(env_a, env_b):
    scope = ["DB_HOST", "DB_PORT"]
    r = build_scope_compare(env_a, env_b, scope)
    in_scope_keys = {e.key for e in r.in_scope}
    assert in_scope_keys == {"DB_HOST", "DB_PORT"}


def test_out_of_scope_keys_flagged(env_a, env_b):
    scope = ["DB_HOST"]
    r = build_scope_compare(env_a, env_b, scope)
    out_keys = {e.key for e in r.out_of_scope}
    assert "APP_ENV" in out_keys
    assert "DB_HOST" not in out_keys


def test_match_count_same_values(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["DB_PORT"])
    assert r.match_count == 1


def test_mismatch_count_different_values(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["DB_HOST", "APP_ENV"])
    assert r.mismatch_count == 2


def test_missing_in_b_value_is_none(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["SECRET"])
    entry = next(e for e in r.entries if e.key == "SECRET")
    assert entry.value_b is None
    assert entry.value_a == "abc"


def test_missing_in_a_value_is_none(env_a, env_b):
    r = build_scope_compare(env_a, env_b, ["NEW_KEY"])
    entry = next(e for e in r.entries if e.key == "NEW_KEY")
    assert entry.value_a is None
    assert entry.value_b == "x"


def test_scope_name_stored(env_a, env_b):
    r = build_scope_compare(env_a, env_b, [], scope_name="staging")
    assert r.scope_name == "staging"


def test_file_names_stored(env_a, env_b):
    r = build_scope_compare(env_a, env_b, [], file_a="a.env", file_b="b.env")
    assert r.file_a == "a.env"
    assert r.file_b == "b.env"


def test_empty_scope_all_out_of_scope(env_a, env_b):
    r = build_scope_compare(env_a, env_b, [])
    assert len(r.in_scope) == 0
    assert len(r.out_of_scope) == len(r.entries)


def test_entries_sorted_alphabetically(env_a, env_b):
    r = build_scope_compare(env_a, env_b, [])
    keys = [e.key for e in r.entries]
    assert keys == sorted(keys)
