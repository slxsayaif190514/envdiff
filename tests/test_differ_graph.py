"""Tests for envdiff.differ_graph."""

import pytest

from envdiff.comparator import CompareResult, KeyDiff
from envdiff.differ_graph import EnvGraph, GraphNode, _extract_prefix, build_graph


def _diff(key: str, val_a: str = "x", val_b: str = "y") -> KeyDiff:
    return KeyDiff(key=key, value_a=val_a, value_b=val_b)


@pytest.fixture
def simple_result() -> CompareResult:
    return CompareResult(
        missing_in_b=[_diff("DB_HOST", "localhost", "")],
        missing_in_a=[_diff("DB_PORT", "", "5432")],
        mismatches=[_diff("DB_NAME", "dev", "prod")],
        matches=[_diff("APP_ENV", "staging", "staging")],
    )


def test_extract_prefix_with_separator():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_separator():
    assert _extract_prefix("HOSTNAME") == ""


def test_extract_prefix_custom_separator():
    assert _extract_prefix("APP.PORT", ".") == "APP"


def test_build_graph_node_count(simple_result):
    graph = build_graph(simple_result)
    assert graph.node_count == 4


def test_build_graph_all_keys_present(simple_result):
    graph = build_graph(simple_result)
    assert "DB_HOST" in graph.nodes
    assert "DB_PORT" in graph.nodes
    assert "DB_NAME" in graph.nodes
    assert "APP_ENV" in graph.nodes


def test_build_graph_issue_flags(simple_result):
    graph = build_graph(simple_result)
    assert graph.nodes["DB_HOST"].has_issue is True
    assert graph.nodes["DB_PORT"].has_issue is True
    assert graph.nodes["DB_NAME"].has_issue is True
    assert graph.nodes["APP_ENV"].has_issue is False


def test_build_graph_edges_for_shared_prefix(simple_result):
    graph = build_graph(simple_result)
    # DB_HOST, DB_PORT, DB_NAME all share prefix DB — 3 edges
    assert graph.edge_count == 3


def test_build_graph_neighbors_linked(simple_result):
    graph = build_graph(simple_result)
    assert "DB_PORT" in graph.nodes["DB_HOST"].neighbors
    assert "DB_NAME" in graph.nodes["DB_HOST"].neighbors


def test_build_graph_no_edges_no_shared_prefix():
    result = CompareResult(
        missing_in_b=[_diff("ALPHA")],
        missing_in_a=[_diff("BETA")],
        mismatches=[],
        matches=[],
    )
    graph = build_graph(result)
    assert graph.edge_count == 0


def test_build_graph_prefixes(simple_result):
    graph = build_graph(simple_result)
    prefixes = graph.prefixes()
    assert "DB" in prefixes
    assert "APP" in prefixes


def test_build_graph_empty_result():
    result = CompareResult(missing_in_b=[], missing_in_a=[], mismatches=[], matches=[])
    graph = build_graph(result)
    assert graph.node_count == 0
    assert graph.edge_count == 0
