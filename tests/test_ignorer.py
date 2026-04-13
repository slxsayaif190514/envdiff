"""Tests for envdiff.ignorer."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.ignorer import IgnoreRules, apply_ignore, build_ignore_rules


@pytest.fixture()
def base_result() -> CompareResult:
    return CompareResult(
        missing_in_b=[KeyDiff("SECRET_KEY", "abc", None), KeyDiff("DEBUG", "1", None)],
        missing_in_a=[KeyDiff("NEW_FEATURE", None, "on")],
        mismatches=[KeyDiff("DB_HOST", "localhost", "prod.db"), KeyDiff("PORT", "5432", "5433")],
        matches=[KeyDiff("APP_NAME", "myapp", "myapp")],
    )


def test_build_ignore_rules_exact():
    rules = build_ignore_rules(keys=["SECRET_KEY", "TOKEN"])
    assert rules.matches("SECRET_KEY")
    assert rules.matches("TOKEN")
    assert not rules.matches("DB_HOST")


def test_build_ignore_rules_patterns():
    rules = build_ignore_rules(patterns=["SECRET_*", "*_TOKEN"])
    assert rules.matches("SECRET_KEY")
    assert rules.matches("API_TOKEN")
    assert not rules.matches("DB_HOST")


def test_build_ignore_rules_combined():
    rules = build_ignore_rules(keys=["PORT"], patterns=["DB_*"])
    assert rules.matches("PORT")
    assert rules.matches("DB_HOST")
    assert not rules.matches("APP_NAME")


def test_ignore_rules_matches_is_case_sensitive():
    rules = build_ignore_rules(keys=["secret_key"])
    assert not rules.matches("SECRET_KEY")
    assert rules.matches("secret_key")


def test_apply_ignore_removes_from_missing_in_b(base_result):
    rules = build_ignore_rules(keys=["SECRET_KEY"])
    result = apply_ignore(base_result, rules)
    keys = [d.key for d in result.missing_in_b]
    assert "SECRET_KEY" not in keys
    assert "DEBUG" in keys


def test_apply_ignore_removes_from_missing_in_a(base_result):
    rules = build_ignore_rules(keys=["NEW_FEATURE"])
    result = apply_ignore(base_result, rules)
    assert result.missing_in_a == []


def test_apply_ignore_removes_from_mismatches(base_result):
    rules = build_ignore_rules(patterns=["DB_*"])
    result = apply_ignore(base_result, rules)
    keys = [d.key for d in result.mismatches]
    assert "DB_HOST" not in keys
    assert "PORT" in keys


def test_apply_ignore_preserves_matches(base_result):
    rules = build_ignore_rules(keys=["SECRET_KEY"])
    result = apply_ignore(base_result, rules)
    assert len(result.matches) == 1
    assert result.matches[0].key == "APP_NAME"


def test_apply_ignore_no_rules_leaves_result_unchanged(base_result):
    rules = build_ignore_rules()
    result = apply_ignore(base_result, rules)
    assert len(result.missing_in_b) == 2
    assert len(result.missing_in_a) == 1
    assert len(result.mismatches) == 2
    assert len(result.matches) == 1
