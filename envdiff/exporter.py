"""Export comparison results to different output formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.comparator import CompareResult

OutputFormat = Literal["json", "csv"]


def export_json(result: CompareResult, indent: int = 2) -> str:
    """Serialize a CompareResult to a JSON string."""
    data: dict = {
        "missing_in_b": [
            {"key": d.key, "value_a": d.value_a}
            for d in result.missing_in_b
        ],
        "missing_in_a": [
            {"key": d.key, "value_b": d.value_b}
            for d in result.missing_in_a
        ],
        "mismatches": [
            {"key": d.key, "value_a": d.value_a, "value_b": d.value_b}
            for d in result.mismatches
        ],
    }
    return json.dumps(data, indent=indent)


def export_csv(result: CompareResult) -> str:
    """Serialize a CompareResult to a CSV string.

    Columns: type, key, value_a, value_b
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["type", "key", "value_a", "value_b"])

    for d in result.missing_in_b:
        writer.writerow(["missing_in_b", d.key, d.value_a, ""])

    for d in result.missing_in_a:
        writer.writerow(["missing_in_a", d.key, "", d.value_b])

    for d in result.mismatches:
        writer.writerow(["mismatch", d.key, d.value_a, d.value_b])

    return buf.getvalue()


def export_result(result: CompareResult, fmt: OutputFormat) -> str:
    """Dispatch to the correct exporter based on *fmt*."""
    if fmt == "json":
        return export_json(result)
    if fmt == "csv":
        return export_csv(result)
    raise ValueError(f"Unsupported export format: {fmt!r}")
