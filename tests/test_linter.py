"""Tests for envdiff.linter."""

import os
import pytest

from envdiff.linter import lint_env_file, LintIssue, LintResult


@pytest.fixture
def tmp_env(tmp_path):
    """Return a helper that writes a .env file and returns its path."""

    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return str(p)

    return _write


def test_clean_file_returns_no_issues(tmp_env):
    path = tmp_env("FOO=bar\nBAZ=qux\n")
    result = lint_env_file(path)
    assert result.is_clean
    assert result.error_count == 0
    assert result.warning_count == 0


def test_missing_separator_is_error(tmp_env):
    path = tmp_env("FOOBAR\n")
    result = lint_env_file(path)
    assert result.error_count == 1
    assert result.issues[0].severity == "error"
    assert "'='" in result.issues[0].message


def test_lowercase_key_is_warning(tmp_env):
    path = tmp_env("foo=bar\n")
    result = lint_env_file(path)
    assert result.warning_count == 1
    assert result.issues[0].severity == "warning"
    assert "uppercase" in result.issues[0].message


def test_duplicate_key_is_error(tmp_env):
    path = tmp_env("FOO=bar\nFOO=baz\n")
    result = lint_env_file(path)
    errors = [i for i in result.issues if i.severity == "error"]
    assert len(errors) == 1
    assert "Duplicate" in errors[0].message
    assert errors[0].key == "FOO"


def test_trailing_whitespace_in_value_is_warning(tmp_env):
    path = tmp_env("FOO=bar   \n")
    result = lint_env_file(path)
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("trailing whitespace" in w.message for w in warnings)


def test_key_whitespace_is_warning(tmp_env):
    path = tmp_env(" FOO =bar\n")
    result = lint_env_file(path)
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("surrounding whitespace" in w.message for w in warnings)


def test_comments_and_blank_lines_ignored(tmp_env):
    path = tmp_env("# comment\n\nFOO=bar\n")
    result = lint_env_file(path)
    assert result.is_clean


def test_missing_file_returns_error():
    result = lint_env_file("/nonexistent/path/.env")
    assert result.error_count == 1
    assert "Cannot read file" in result.issues[0].message


def test_lint_result_filename_stored(tmp_env):
    path = tmp_env("FOO=bar\n")
    result = lint_env_file(path)
    assert result.filename == path


def test_issue_repr():
    issue = LintIssue(5, "MY_KEY", "some message", "warning")
    r = repr(issue)
    assert "line 5" in r
    assert "MY_KEY" in r
    assert "warning" in r
