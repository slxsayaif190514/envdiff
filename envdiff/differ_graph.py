"""Build a dependency graph from env keys using naming conventions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envdiff.comparator import CompareResult


@dataclass
class GraphNode:
    key: str
    prefix: str
    neighbors: List[str] = field(default_factory=list)
    has_issue: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        return f"GraphNode(key={self.key!r}, prefix={self.prefix!r}, has_issue={self.has_issue})"


@dataclass
class EnvGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    edges: List[tuple[str, str]] = field(default_factory=list)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def prefixes(self) -> Set[str]:
        return {n.prefix for n in self.nodes.values()}


def _extract_prefix(key: str, separator: str = "_") -> str:
    parts = key.split(separator, 1)
    return parts[0] if len(parts) > 1 else ""


def build_graph(result: CompareResult, separator: str = "_") -> EnvGraph:
    """Build an EnvGraph from a CompareResult.

    Nodes represent individual env keys. Edges connect keys that share
    the same prefix, indicating they belong to the same logical group.
    Nodes are flagged as having issues when they appear in any diff list.
    """
    graph = EnvGraph()

    issue_keys: Set[str] = set()
    issue_keys.update(d.key for d in result.missing_in_b)
    issue_keys.update(d.key for d in result.missing_in_a)
    issue_keys.update(d.key for d in result.mismatches)

    all_keys: Set[str] = set()
    all_keys.update(d.key for d in result.missing_in_b)
    all_keys.update(d.key for d in result.missing_in_a)
    all_keys.update(d.key for d in result.mismatches)
    all_keys.update(d.key for d in result.matches)

    for key in sorted(all_keys):
        prefix = _extract_prefix(key, separator)
        graph.nodes[key] = GraphNode(
            key=key,
            prefix=prefix,
            has_issue=key in issue_keys,
        )

    prefix_map: Dict[str, List[str]] = {}
    for key, node in graph.nodes.items():
        if node.prefix:
            prefix_map.setdefault(node.prefix, []).append(key)

    for prefix, keys in prefix_map.items():
        for i, a in enumerate(keys):
            for b in keys[i + 1 :]:
                graph.edges.append((a, b))
                graph.nodes[a].neighbors.append(b)
                graph.nodes[b].neighbors.append(a)

    return graph
