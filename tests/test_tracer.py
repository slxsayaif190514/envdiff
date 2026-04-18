import pytest
from envdiff.tracer import trace_key, TraceResult, TraceEntry


ENV_A = {"DB_HOST": "localhost", "PORT": "5432"}
ENV_B = {"DB_HOST": "prod.db", "DEBUG": "false"}
ENV_C = {"DB_HOST": "staging.db"}


def test_key_not_in_any_env():
    result = trace_key("MISSING", [ENV_A, ENV_B], ["a", "b"])
    assert isinstance(result, TraceResult)
    assert result.entries == []
    assert result.resolved_value is None
    assert result.resolved_source is None


def test_key_in_one_env():
    result = trace_key("PORT", [ENV_A, ENV_B], ["a", "b"])
    assert result.source_count == 1
    assert result.resolved_value == "5432"
    assert result.resolved_source == "a"
    assert not result.is_overridden


def test_key_overridden_once():
    result = trace_key("DB_HOST", [ENV_A, ENV_B], ["a", "b"])
    assert result.source_count == 2
    assert result.resolved_value == "prod.db"
    assert result.resolved_source == "b"
    assert result.is_overridden
    assert result.entries[0].overridden_by == "b"
    assert result.entries[1].overridden_by is None


def test_key_overridden_multiple_times():
    result = trace_key("DB_HOST", [ENV_A, ENV_B, ENV_C], ["a", "b", "c"])
    assert result.source_count == 3
    assert result.resolved_value == "staging.db"
    assert result.entries[0].overridden_by == "b"
    assert result.entries[1].overridden_by == "c"
    assert result.entries[2].overridden_by is None


def test_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        trace_key("KEY", [ENV_A], ["a", "b"])


def test_trace_entry_repr():
    e = TraceEntry(key="FOO", source="x.env", value="bar")
    assert "FOO" in repr(e)
    assert "x.env" in repr(e)
