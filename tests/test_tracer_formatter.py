from envdiff.tracer import trace_key
from envdiff.tracer_formatter import format_trace_result


ENV_A = {"DB_HOST": "localhost", "PORT": "5432"}
ENV_B = {"DB_HOST": "prod.db"}


def _strip(s: str) -> str:
    """Strip ANSI codes for easier assertion."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_header_contains_key():
    result = trace_key("DB_HOST", [ENV_A, ENV_B], ["a.env", "b.env"])
    out = _strip(format_trace_result(result))
    assert "DB_HOST" in out


def test_not_found_message():
    result = trace_key("MISSING", [ENV_A], ["a.env"])
    out = _strip(format_trace_result(result))
    assert "not found" in out


def test_resolved_value_shown():
    result = trace_key("DB_HOST", [ENV_A, ENV_B], ["a.env", "b.env"])
    out = _strip(format_trace_result(result))
    assert "prod.db" in out
    assert "resolved" in out


def test_overridden_source_shown():
    result = trace_key("DB_HOST", [ENV_A, ENV_B], ["a.env", "b.env"])
    out = _strip(format_trace_result(result))
    assert "overridden" in out
    assert "a.env" in out


def test_source_count_shown():
    result = trace_key("DB_HOST", [ENV_A, ENV_B], ["a.env", "b.env"])
    out = _strip(format_trace_result(result))
    assert "2" in out
