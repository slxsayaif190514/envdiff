from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PromoteEntry:
    key: str
    value: str
    source_env: str
    target_env: str
    overwritten_value: Optional[str] = None

    def __repr__(self) -> str:
        return f"PromoteEntry({self.key!r}: {self.source_env!r} -> {self.target_env!r})"


@dataclass
class PromoteResult:
    source: str
    target: str
    promoted: List[PromoteEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def promote_count(self) -> int:
        return len(self.promoted)

    @property
    def skip_count(self) -> int:
        return len(self.skipped)

    @property
    def is_empty(self) -> bool:
        return self.promote_count == 0


def promote_keys(
    source_env: Dict[str, str],
    target_env: Dict[str, str],
    keys: List[str],
    source_name: str = "source",
    target_name: str = "target",
    overwrite: bool = True,
) -> PromoteResult:
    result = PromoteResult(source=source_name, target=target_name)

    for key in keys:
        if key not in source_env:
            result.skipped.append(key)
            continue

        value = source_env[key]
        existing = target_env.get(key)

        if existing is not None and not overwrite:
            result.skipped.append(key)
            continue

        entry = PromoteEntry(
            key=key,
            value=value,
            source_env=source_name,
            target_env=target_name,
            overwritten_value=existing if existing != value else None,
        )
        result.promoted.append(entry)

    result.promoted.sort(key=lambda e: e.key)
    result.skipped.sort()
    return result
