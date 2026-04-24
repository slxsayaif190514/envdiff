"""Cross-environment matrix comparison: compare N env files pairwise."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from envdiff.comparator import CompareResult, compare


@dataclass
class MatrixCell:
    file_a: str
    file_b: str
    result: CompareResult

    @property
    def has_issues(self) -> bool:
        return bool(
            self.result.missing_in_b
            or self.result.missing_in_a
            or self.result.mismatches
        )

    @property
    def issue_count(self) -> int:
        return (
            len(self.result.missing_in_b)
            + len(self.result.missing_in_a)
            + len(self.result.mismatches)
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"MatrixCell({self.file_a!r} vs {self.file_b!r}, issues={self.issue_count})"


@dataclass
class MatrixResult:
    files: List[str]
    cells: List[MatrixCell] = field(default_factory=list)

    @property
    def pair_count(self) -> int:
        return len(self.cells)

    @property
    def clean_pairs(self) -> List[MatrixCell]:
        return [c for c in self.cells if not c.has_issues]

    @property
    def dirty_pairs(self) -> List[MatrixCell]:
        return [c for c in self.cells if c.has_issues]

    def get(self, file_a: str, file_b: str) -> MatrixCell | None:
        for cell in self.cells:
            if cell.file_a == file_a and cell.file_b == file_b:
                return cell
        return None


def build_matrix(envs: Dict[str, Dict[str, str]]) -> MatrixResult:
    """Compare every ordered pair (a, b) where a != b."""
    names = list(envs.keys())
    cells: List[MatrixCell] = []
    for i, name_a in enumerate(names):
        for name_b in names[i + 1:]:
            result = compare(envs[name_a], envs[name_b])
            cells.append(MatrixCell(file_a=name_a, file_b=name_b, result=result))
    return MatrixResult(files=names, cells=cells)
