"""Lint .env files for common style and correctness issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str | None
    message: str
    severity: str  # 'error' | 'warning'

    def __repr__(self) -> str:
        loc = f"line {self.line_number}"
        key_part = f" [{self.key}]" if self.key else ""
        return f"LintIssue({self.severity}, {loc}{key_part}: {self.message})"


@dataclass
class LintResult:
    filename: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


def lint_env_file(path: str) -> LintResult:
    """Read a .env file and return a LintResult with any style/correctness issues."""
    result = LintResult(filename=path)

    try:
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError as exc:
        result.issues.append(LintIssue(0, None, f"Cannot read file: {exc}", "error"))
        return result

    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Must contain '='
        if "=" not in line:
            result.issues.append(LintIssue(lineno, None, "Line has no '=' separator", "error"))
            continue

        key, _, value = line.partition("=")

        # Key should not have leading/trailing whitespace
        if key != key.strip():
            result.issues.append(LintIssue(lineno, key.strip(), "Key has surrounding whitespace", "warning"))
            key = key.strip()

        # Key should be uppercase
        if key and key != key.upper():
            result.issues.append(LintIssue(lineno, key, "Key is not uppercase", "warning"))

        # Duplicate key detection
        if key in seen_keys:
            result.issues.append(
                LintIssue(lineno, key, f"Duplicate key (first seen on line {seen_keys[key]})", "error")
            )
        else:
            seen_keys[key] = lineno

        # Value trailing whitespace
        if value != value.rstrip():
            result.issues.append(LintIssue(lineno, key, "Value has trailing whitespace", "warning"))

    return result
