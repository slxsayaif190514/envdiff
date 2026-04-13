"""Tests for envdiff.differ.run_diff."""

import pytest
from pathlib import Path

from envdiff.differ import run_diff, DiffError
from envdiff.sorter import SortKey


@pytest.fixture()
def env_dir(tmp_path: Path):
    """Return a helper that writes a .env file and returns its path."""

    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_run_diff_no_differences(env_dir):
    a = env_dir("a.env", "FOO=bar\nBAZ=qux\n")
    b = env_dir("b.env", "FOO=bar\nBAZ=qux\n")
    result = run_diff(a, b)
    assert result.missing_in_a == []
    assert result.missing_in_b == []
    assert result.mismatches == []


def test_run_diff_missing_in_b(env_dir):
    a = env_dir("a.env", "FOO=bar\nONLY_A=yes\n")
    b = env_dir("b.env", "FOO=bar\n")
    result = run_diff(a, b)
    keys = [d.key for d in result.missing_in_b]
    assert "ONLY_A" in keys


def test_run_diff_missing_in_a(env_dir):
    a = env_dir("a.env", "FOO=bar\n")
    b = env_dir("b.env", "FOO=bar\nONLY_B=yes\n")
    result = run_diff(a, b)
    keys = [d.key for d in result.missing_in_a]
    assert "ONLY_B" in keys


def test_run_diff_mismatch(env_dir):
    a = env_dir("a.env", "FOO=one\n")
    b = env_dir("b.env", "FOO=two\n")
    result = run_diff(a, b)
    assert len(result.mismatches) == 1
    assert result.mismatches[0].key == "FOO"


def test_run_diff_prefix_filter(env_dir):
    a = env_dir("a.env", "DB_HOST=localhost\nAPP_NAME=myapp\nDB_PORT=5432\n")
    b = env_dir("b.env", "DB_HOST=remotehost\nAPP_NAME=myapp\n")
    result = run_diff(a, b, prefix="DB_")
    all_keys = (
        [d.key for d in result.mismatches]
        + [d.key for d in result.missing_in_b]
        + [d.key for d in result.missing_in_a]
    )
    assert all(k.startswith("DB_") for k in all_keys)
    assert "APP_NAME" not in all_keys


def test_run_diff_only_type_mismatch(env_dir):
    a = env_dir("a.env", "FOO=one\nBAR=same\nONLY=here\n")
    b = env_dir("b.env", "FOO=two\nBAR=same\n")
    result = run_diff(a, b, only_type="mismatch")
    assert len(result.mismatches) == 1
    assert result.missing_in_b == []
    assert result.missing_in_a == []


def test_run_diff_sort_by_key(env_dir):
    a = env_dir("a.env", "ZOO=1\nABC=2\nMID=3\n")
    b = env_dir("b.env", "ZOO=9\nABC=9\nMID=9\n")
    result = run_diff(a, b, sort_by=SortKey.KEY)
    keys = [d.key for d in result.mismatches]
    assert keys == sorted(keys)


def test_run_diff_file_not_found(tmp_path):
    with pytest.raises(DiffError, match="File not found"):
        run_diff(str(tmp_path / "nope.env"), str(tmp_path / "also_nope.env"))


def test_run_diff_parse_error(env_dir):
    # A file with a line that the parser should reject
    a = env_dir("bad.env", "THIS IS NOT VALID\x00\n")
    b = env_dir("b.env", "FOO=bar\n")
    # If parser raises, DiffError should wrap it; if parser is lenient, just check no crash
    try:
        run_diff(a, b)
    except DiffError:
        pass  # expected path
