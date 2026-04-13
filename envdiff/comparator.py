"""Compare two parsed env dicts and produce structured diffs."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyDiff:
    key: str
    value_a: Optional[str]
    value_b: Optional[str]

    def __repr__(self) -> str:  # noqa: D105
        return f"KeyDiff(key={self.key!r}, a={self.value_a!r}, b={self.value_b!r})"


@dataclass
class CompareResult:
    diffs: List[KeyDiff] = field(default_factory=list)
    matched_count: int = 0

    @property
    def missing_in_b(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.value_b is None]

    @property
    def missing_in_a(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.value_a is None]

    @property
    def mismatches(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.value_a is not None and d.value_b is not None]

    @property
    def has_differences(self) -> bool:
        return bool(self.diffs)


def compare(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
) -> CompareResult:
    """Compare two env dicts and return a CompareResult."""
    diffs: List[KeyDiff] = []
    matched = 0

    all_keys = set(env_a) | set(env_b)

    for key in sorted(all_keys):
        val_a = env_a.get(key)
        val_b = env_b.get(key)

        if val_a is None:
            diffs.append(KeyDiff(key=key, value_a=None, value_b=val_b))
        elif val_b is None:
            diffs.append(KeyDiff(key=key, value_a=val_a, value_b=None))
        elif val_a != val_b:
            diffs.append(KeyDiff(key=key, value_a=val_a, value_b=val_b))
        else:
            matched += 1

    return CompareResult(diffs=diffs, matched_count=matched)
