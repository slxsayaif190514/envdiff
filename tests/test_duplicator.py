"""Tests for envdiff.duplicator."""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.duplicator import find_duplicates, DuplicateResult, DuplicateEntry


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p
    return _write


def test_clean_file_no_duplicates(tmp_env):
    p = tmp_env("FOO=bar\nBAZ=qux\n")
    result = find_duplicates(p)
    assert result.is_clean
    assert result.duplicate_count == 0


def test_single_duplicate_same_value(tmp_env):
    p = tmp_env("FOO=bar\nFOO=bar\n")
    result = find_duplicates(p)
    assert not result.is_clean
    assert result.duplicate_count == 1
    assert result.conflict_count == 0


def test_single_duplicate_different_values(tmp_env):
    p = tmp_env("FOO=bar\nFOO=baz\n")
    result = find_duplicates(p)
    assert result.duplicate_count == 1
    assert result.conflict_count == 1
    dup = result.duplicates[0]
    assert dup.value_conflict
    assert dup.key == "FOO"
    assert dup.lines == [1, 2]
    assert dup.values == ["bar", "baz"]


def test_multiple_duplicates(tmp_env):
    content = "A=1\nB=2\nA=3\nB=2\nC=5\n"
    p = tmp_env(content)
    result = find_duplicates(p)
    assert result.duplicate_count == 2
    keys = [d.key for d in result.duplicates]
    assert "A" in keys
    assert "B" in keys


def test_comments_and_blanks_ignored(tmp_env):
    content = "# comment\n\nFOO=bar\n# another\nFOO=bar\n"
    p = tmp_env(content)
    result = find_duplicates(p)
    assert result.duplicate_count == 1
    assert result.duplicates[0].lines == [3, 5]


def test_quoted_values_stripped(tmp_env):
    p = tmp_env('KEY="hello"\nKEY=hello\n')
    result = find_duplicates(p)
    dup = result.duplicates[0]
    assert dup.values == ["hello", "hello"]
    assert not dup.value_conflict


def test_filename_stored(tmp_env):
    p = tmp_env("X=1\n")
    result = find_duplicates(p)
    assert result.filename == str(p)


def test_three_occurrences(tmp_env):
    p = tmp_env("K=a\nK=b\nK=c\n")
    result = find_duplicates(p)
    dup = result.duplicates[0]
    assert len(dup.lines) == 3
    assert dup.value_conflict
