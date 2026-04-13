"""Generate patch suggestions to reconcile differences between two env files."""

from dataclasses import dataclass, field
from typing import List
from envdiff.comparator import CompareResult, KeyDiff


@dataclass
class PatchLine:
    key: str
    action: str  # 'add', 'remove', 'update'
    value: str
    comment: str = ""

    def __repr__(self) -> str:
        return f"PatchLine(key={self.key!r}, action={self.action!r}, value={self.value!r})"


@dataclass
class PatchResult:
    source_label: str
    target_label: str
    lines: List[PatchLine] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.lines) == 0

    @property
    def action_count(self) -> int:
        return len(self.lines)


def build_patch(result: CompareResult, source_label: str = "a", target_label: str = "b") -> PatchResult:
    """Build a patch that would make target_label match source_label."""
    patch = PatchResult(source_label=source_label, target_label=target_label)

    for diff in result.missing_in_b:
        patch.lines.append(PatchLine(
            key=diff.key,
            action="add",
            value=diff.value_a,
            comment=f"present in {source_label}, missing in {target_label}",
        ))

    for diff in result.missing_in_a:
        patch.lines.append(PatchLine(
            key=diff.key,
            action="remove",
            value=diff.value_b,
            comment=f"present in {target_label}, not in {source_label}",
        ))

    for diff in result.mismatches:
        patch.lines.append(PatchLine(
            key=diff.key,
            action="update",
            value=diff.value_a,
            comment=f"change from {diff.value_b!r} to {diff.value_a!r}",
        ))

    patch.lines.sort(key=lambda pl: pl.key)
    return patch


def format_patch(patch: PatchResult) -> str:
    """Render a patch as a human-readable string."""
    if patch.is_empty:
        return f"# No changes needed — {patch.target_label} already matches {patch.source_label}\n"

    lines = [f"# Patch: apply to {patch.target_label} to match {patch.source_label}\n"]
    for pl in patch.lines:
        if pl.action == "add":
            lines.append(f"{pl.key}={pl.value}  # ADD: {pl.comment}")
        elif pl.action == "remove":
            lines.append(f"# REMOVE {pl.key}={pl.value}  # {pl.comment}")
        elif pl.action == "update":
            lines.append(f"{pl.key}={pl.value}  # UPDATE: {pl.comment}")
    return "\n".join(lines) + "\n"
