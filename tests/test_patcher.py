"""Tests for envdiff.patcher."""

import pytest
from envdiff.comparator import CompareResult, KeyDiff
from envdiff.patcher import PatchLine, PatchResult, build_patch, format_patch


def _diff(key, a=None, b=None):
    return KeyDiff(key=key, value_a=a, value_b=b)


@pytest.fixture
def empty_result():
    return CompareResult(missing_in_a=[], missing_in_b=[], mismatches=[])


@pytest.fixture
def full_result():
    return CompareResult(
        missing_in_b=[_diff("ONLY_A", a="alpha")],
        missing_in_a=[_diff("ONLY_B", b="beta")],
        mismatches=[_diff("SHARED", a="new_val", b="old_val")],
    )


def test_patch_empty_when_no_differences(empty_result):
    patch = build_patch(empty_result)
    assert patch.is_empty
    assert patch.action_count == 0


def test_patch_add_for_missing_in_b(full_result):
    patch = build_patch(full_result)
    adds = [pl for pl in patch.lines if pl.action == "add"]
    assert len(adds) == 1
    assert adds[0].key == "ONLY_A"
    assert adds[0].value == "alpha"


def test_patch_remove_for_missing_in_a(full_result):
    patch = build_patch(full_result)
    removes = [pl for pl in patch.lines if pl.action == "remove"]
    assert len(removes) == 1
    assert removes[0].key == "ONLY_B"
    assert removes[0].value == "beta"


def test_patch_update_for_mismatches(full_result):
    patch = build_patch(full_result)
    updates = [pl for pl in patch.lines if pl.action == "update"]
    assert len(updates) == 1
    assert updates[0].key == "SHARED"
    assert updates[0].value == "new_val"


def test_patch_lines_sorted_alphabetically(full_result):
    patch = build_patch(full_result)
    keys = [pl.key for pl in patch.lines]
    assert keys == sorted(keys)


def test_patch_labels_stored(full_result):
    patch = build_patch(full_result, source_label="prod", target_label="staging")
    assert patch.source_label == "prod"
    assert patch.target_label == "staging"


def test_format_patch_empty(empty_result):
    patch = build_patch(empty_result, source_label="a", target_label="b")
    output = format_patch(patch)
    assert "No changes needed" in output
    assert "b" in output


def test_format_patch_contains_add(full_result):
    patch = build_patch(full_result)
    output = format_patch(patch)
    assert "ONLY_A=alpha" in output
    assert "ADD" in output


def test_format_patch_contains_remove(full_result):
    patch = build_patch(full_result)
    output = format_patch(patch)
    assert "REMOVE" in output
    assert "ONLY_B" in output


def test_format_patch_contains_update(full_result):
    patch = build_patch(full_result)
    output = format_patch(patch)
    assert "SHARED=new_val" in output
    assert "UPDATE" in output


def test_patch_line_repr():
    pl = PatchLine(key="FOO", action="add", value="bar")
    assert "FOO" in repr(pl)
    assert "add" in repr(pl)
