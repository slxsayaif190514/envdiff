"""Format ClusterResult for terminal output."""
from __future__ import annotations
from envdiff.differ_cluster import ClusterResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def format_cluster_result(result: ClusterResult, show_values: bool = False) -> str:
    lines: list[str] = []
    header = _bold(f"Value Clusters — {result.filename}")
    lines.append(header)
    lines.append(
        f"  {_cyan(str(result.cluster_count))} clusters, "
        f"{_cyan(str(result.total_keys))} total keys, "
        f"{_yellow(str(result.shared_count))} shared, "
        f"{_dim(str(result.singleton_count))} unique"
    )
    lines.append("")

    for cluster in result.clusters:
        if len(cluster.keys) > 1:
            label = _yellow(f"[shared by {len(cluster.keys)} keys]")
        else:
            label = _dim("[unique]")

        if show_values:
            value_display = _dim(repr(cluster.value[:40]))
            lines.append(f"  {label} value={value_display}")
        else:
            lines.append(f"  {label}")

        for key in cluster.keys:
            lines.append(f"    {_green(key)}")

    return "\n".join(lines)
