import pytest
from envdiff.cascader import cascade_envs, CascadeEntry, CascadeResult
from envdiff.cascader_formatter import format_cascade_result


ENV_BASE = {"APP_HOST": "localhost", "APP_PORT": "5000", "DEBUG": "false"}
ENV_PROD = {"APP_HOST": "prod.example.com", "DEBUG": "false", "SECRET": "abc"}
ENV_OVERRIDE = {"APP_PORT": "8080"}


def test_empty_input_returns_empty_result():
    result = cascade_envs([])
    assert result.key_count == 0
    assert result.sources == []


def test_single_env_no_overrides():
    result = cascade_envs([("base.env", ENV_BASE)])
    assert result.key_count == 3
    assert result.override_count == 0
    assert result.resolved["APP_PORT"] == "5000"


def test_later_env_wins_on_conflict():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    assert result.resolved["APP_HOST"] == "prod.example.com"


def test_override_count_incremented_on_value_change():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    # APP_HOST changes; DEBUG stays same — only 1 override
    assert result.override_count == 1


def test_same_value_not_counted_as_override():
    result = cascade_envs([("a.env", {"K": "v"}), ("b.env", {"K": "v"})])
    assert result.override_count == 0


def test_keys_from_all_sources_merged():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    assert "SECRET" in result.resolved
    assert "APP_PORT" in result.resolved


def test_entry_source_reflects_winning_file():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    entry = next(e for e in result.entries if e.key == "APP_HOST")
    assert entry.source == "prod.env"


def test_non_overridden_entry_has_no_overridden_by():
    result = cascade_envs([("base.env", ENV_BASE), ("extra.env", ENV_OVERRIDE)])
    entry = next(e for e in result.entries if e.key == "APP_HOST")
    assert entry.overridden_by is None


def test_overridden_entry_records_source():
    result = cascade_envs([("base.env", ENV_BASE), ("extra.env", ENV_OVERRIDE)])
    entry = next(e for e in result.entries if e.key == "APP_PORT")
    assert entry.overridden_by == "extra.env"


def test_has_overrides_property():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    assert result.has_overrides is True


def test_formatter_contains_key_names():
    result = cascade_envs([("base.env", ENV_BASE)])
    output = format_cascade_result(result, no_color=True)
    assert "APP_HOST" in output
    assert "APP_PORT" in output


def test_formatter_shows_override_count():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    output = format_cascade_result(result, no_color=True)
    assert "1" in output


def test_formatter_shows_sources():
    result = cascade_envs([("base.env", ENV_BASE), ("prod.env", ENV_PROD)])
    output = format_cascade_result(result, no_color=True)
    assert "base.env" in output
    assert "prod.env" in output
