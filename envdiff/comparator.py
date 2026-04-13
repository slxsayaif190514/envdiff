"""Core comparison logic for envdiff."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyDiff:
    key: str
    status: str  # 'missing_in', 'extra_in', 'mismatch'
    env_a_value: Optional[str] = None
    env_b_value: Optional[str] = None

    def __repr__(self) -> str:
        if self.status == "mismatch":
            return (
                f"KeyDiff({self.key!r}, mismatch: "
                f"{self.env_a_value!r} vs {self.env_b_value!r})"
            )
        return f"KeyDiff({self.key!r}, {self.status})"


@dataclass
class CompareResult:
    env_a_name: str
    env_b_name: str
    diffs: List[KeyDiff] = field(default_factory=list)

    @property
    def missing_in_b(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.status == "missing_in_b"]

    @property
    def missing_in_a(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.status == "missing_in_a"]

    @property
    def mismatches(self) -> List[KeyDiff]:
        return [d for d in self.diffs if d.status == "mismatch"]

    @property
    def has_differences(self) -> bool:
        return len(self.diffs) > 0


def compare_envs(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    env_a_name: str = "env_a",
    env_b_name: str = "env_b",
    keys_only: bool = False,
) -> CompareResult:
    """Compare two parsed env dicts and return a CompareResult.

    Args:
        env_a: dict from the first env file
        env_b: dict from the second env file
        env_a_name: label for the first env
        env_b_name: label for the second env
        keys_only: if True, skip value comparison (only check key presence)
    """
    result = CompareResult(env_a_name=env_a_name, env_b_name=env_b_name)

    all_keys = set(env_a) | set(env_b)

    for key in sorted(all_keys):
        in_a = key in env_a
        in_b = key in env_b

        if in_a and not in_b:
            result.diffs.append(KeyDiff(key=key, status="missing_in_b", env_a_value=env_a[key]))
        elif in_b and not in_a:
            result.diffs.append(KeyDiff(key=key, status="missing_in_a", env_b_value=env_b[key]))
        elif not keys_only and env_a[key] != env_b[key]:
            result.diffs.append(
                KeyDiff(
                    key=key,
                    status="mismatch",
                    env_a_value=env_a[key],
                    env_b_value=env_b[key],
                )
            )

    return result
