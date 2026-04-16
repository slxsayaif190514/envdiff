import pytest
from envdiff.interpolator import (
    interpolate_env,
    InterpolationResult,
    InterpolationIssue,
    _refs_in_value,
    _resolve_value,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs: str) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# _refs_in_value
# ---------------------------------------------------------------------------

def test_refs_in_value_brace_syntax():
    assert _refs_in_value("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_refs_in_value_dollar_syntax():
    assert _refs_in_value("$HOST:$PORT") == ["HOST", "PORT"]


def test_refs_in_value_no_refs():
    assert _refs_in_value("plain-value") == []


def test_refs_in_value_mixed_syntax():
    refs = _refs_in_value("${SCHEME}://$HOST")
    assert refs == ["SCHEME", "HOST"]


# ---------------------------------------------------------------------------
# _resolve_value
# ---------------------------------------------------------------------------

def test_resolve_value_known_ref():
    env = {"HOST": "localhost"}
    assert _resolve_value("${HOST}:5432", env) == "localhost:5432"


def test_resolve_value_unknown_ref_left_as_is():
    result = _resolve_value("${MISSING}", {})
    assert result == "${MISSING}"


# ---------------------------------------------------------------------------
# interpolate_env
# ---------------------------------------------------------------------------

def test_clean_env_no_refs():
    result = interpolate_env(_env(FOO="bar", BAZ="qux"))
    assert result.is_clean
    assert result.unresolved_count == 0
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}


def test_resolved_value_substituted():
    env = _env(HOST="db.local", DSN="postgres://${HOST}/mydb")
    result = interpolate_env(env)
    assert result.resolved["DSN"] == "postgres://db.local/mydb"


def test_issue_recorded_for_ref():
    env = _env(HOST="db.local", DSN="${HOST}:5432")
    result = interpolate_env(env)
    issue_keys = [i.key for i in result.issues]
    assert "DSN" in issue_keys


def test_resolved_ref_has_value():
    env = _env(HOST="db.local", DSN="${HOST}")
    result = interpolate_env(env)
    issue = next(i for i in result.issues if i.key == "DSN")
    assert issue.resolved == "db.local"


def test_unresolved_ref_is_none():
    env = _env(DSN="${MISSING_HOST}:5432")
    result = interpolate_env(env)
    assert result.unresolved_count == 1
    issue = result.issues[0]
    assert issue.ref == "MISSING_HOST"
    assert issue.resolved is None


def test_multiple_refs_in_one_value():
    env = _env(SCHEME="https", HOST="example.com", URL="${SCHEME}://${HOST}/path")
    result = interpolate_env(env)
    assert result.resolved["URL"] == "https://example.com/path"
    url_issues = [i for i in result.issues if i.key == "URL"]
    assert len(url_issues) == 2


def test_is_clean_false_when_issues_exist():
    env = _env(DSN="${MISSING}")
    result = interpolate_env(env)
    assert not result.is_clean
