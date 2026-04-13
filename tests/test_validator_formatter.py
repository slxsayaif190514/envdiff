"""Tests for envdiff.validator_formatter."""
from envdiff.validator import ValidationResult
from envdiff.validator_formatter import format_validation_result


def _plain(s: str) -> str:
    """Strip ANSI codes for easier assertion."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_valid_result_shows_pass():
    result = ValidationResult()
    output = _plain(format_validation_result(result))
    assert "Validation passed" in output


def test_valid_result_includes_filename():
    result = ValidationResult()
    output = _plain(format_validation_result(result, filename=".env.prod"))
    assert ".env.prod" in output


def test_missing_required_shown():
    result = ValidationResult(missing_required=["SECRET_KEY", "DB_PASS"])
    output = _plain(format_validation_result(result))
    assert "SECRET_KEY" in output
    assert "DB_PASS" in output
    assert "Missing required" in output


def test_unknown_keys_shown():
    result = ValidationResult(unknown_keys=["LEGACY_FLAG"])
    output = _plain(format_validation_result(result))
    assert "LEGACY_FLAG" in output
    assert "Unknown keys" in output


def test_type_errors_shown():
    result = ValidationResult(type_errors={"PORT": "expected type 'int', got value 'abc'"})
    output = _plain(format_validation_result(result))
    assert "PORT" in output
    assert "Type validation errors" in output


def test_issue_count_in_header():
    result = ValidationResult(
        missing_required=["A"],
        unknown_keys=["B"],
        type_errors={"C": "bad"},
    )
    output = _plain(format_validation_result(result))
    assert "3 found" in output


def test_no_filename_no_label():
    result = ValidationResult(missing_required=["X"])
    output = _plain(format_validation_result(result))
    assert "for" not in output
