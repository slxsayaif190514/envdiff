"""Tests for envdiff.tagger_formatter"""
from envdiff.tagger import TagEntry, TagResult
from envdiff.tagger_formatter import format_tag_result


def _make(tagged=None, untagged=None, filename=".env"):
    entries = [TagEntry(key=k, tags=t) for k, t in (tagged or {}).items()]
    return TagResult(filename=filename, entries=entries, untagged=untagged or [])


def test_header_contains_filename():
    result = _make(filename=".env.staging")
    out = format_tag_result(result, color=False)
    assert ".env.staging" in out


def test_tagged_count_shown():
    result = _make(tagged={"DB_HOST": ["db"], "DB_PASS": ["db", "secret"]})
    out = format_tag_result(result, color=False)
    assert "2" in out


def test_tagged_key_appears():
    result = _make(tagged={"APP_PORT": ["app"]})
    out = format_tag_result(result, color=False)
    assert "APP_PORT" in out
    assert "app" in out


def test_untagged_key_appears():
    result = _make(untagged=["MYSTERY_KEY"])
    out = format_tag_result(result, color=False)
    assert "MYSTERY_KEY" in out


def test_fully_tagged_message():
    result = _make(tagged={"ONLY": ["x"]}, untagged=[])
    out = format_tag_result(result, color=False)
    assert "All keys are tagged" in out


def test_no_fully_tagged_message_when_untagged():
    result = _make(untagged=["LEFTOVER"])
    out = format_tag_result(result, color=False)
    assert "All keys are tagged" not in out
