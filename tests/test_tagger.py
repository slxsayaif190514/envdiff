"""Tests for envdiff.tagger"""
import pytest
from envdiff.tagger import tag_env, TagEntry, TagResult


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "APP_DEBUG": "true",
        "APP_PORT": "8080",
        "UNRELATED": "value",
    }


def test_matching_prefix_rule(base_env):
    rules = {"DB_*": ["database"]}
    result = tag_env(base_env, rules)
    keys = [e.key for e in result.entries]
    assert "DB_HOST" in keys
    assert "DB_PASSWORD" in keys


def test_untagged_keys_listed(base_env):
    rules = {"DB_*": ["database"]}
    result = tag_env(base_env, rules)
    assert "APP_DEBUG" in result.untagged
    assert "UNRELATED" in result.untagged


def test_multiple_tags_for_key(base_env):
    rules = {"DB_PASSWORD": ["database", "secret"]}
    result = tag_env(base_env, rules)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "database" in entry.tags
    assert "secret" in entry.tags


def test_overlapping_patterns_merge_tags(base_env):
    rules = {"DB_*": ["database"], "*PASSWORD*": ["sensitive"]}
    result = tag_env(base_env, rules)
    entry = next(e for e in result.entries if e.key == "DB_PASSWORD")
    assert "database" in entry.tags
    assert "sensitive" in entry.tags


def test_no_rules_all_untagged(base_env):
    result = tag_env(base_env, {})
    assert result.tagged_count == 0
    assert len(result.untagged) == len(base_env)


def test_is_fully_tagged_when_all_match(base_env):
    rules = {"*": ["all"]}
    result = tag_env(base_env, rules)
    assert result.is_fully_tagged


def test_is_not_fully_tagged_with_leftover(base_env):
    rules = {"DB_*": ["database"]}
    result = tag_env(base_env, rules)
    assert not result.is_fully_tagged


def test_filename_stored(base_env):
    result = tag_env(base_env, {}, filename=".env.prod")
    assert result.filename == ".env.prod"


def test_tagged_count(base_env):
    rules = {"APP_*": ["app"]}
    result = tag_env(base_env, rules)
    assert result.tagged_count == 2
