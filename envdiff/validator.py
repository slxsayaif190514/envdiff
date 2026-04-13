"""Validate .env file keys against a schema or required key list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    unknown_keys: List[str] = field(default_factory=list)
    type_errors: Dict[str, str] = field(default_factory=dict)  # key -> message

    @property
    def is_valid(self) -> bool:
        return (
            not self.missing_required
            and not self.unknown_keys
            and not self.type_errors
        )

    @property
    def issue_count(self) -> int:
        return len(self.missing_required) + len(self.unknown_keys) + len(self.type_errors)


# Simple type validators
_TYPE_VALIDATORS = {
    "int": lambda v: v.lstrip("-").isdigit(),
    "bool": lambda v: v.lower() in ("true", "false", "1", "0", "yes", "no"),
    "url": lambda v: v.startswith(("http://", "https://")),
    "nonempty": lambda v: len(v.strip()) > 0,
}


def validate_env(
    env: Dict[str, str],
    required: Optional[List[str]] = None,
    schema: Optional[Dict[str, str]] = None,
    allow_unknown: bool = True,
) -> ValidationResult:
    """Validate an env dict against required keys and an optional type schema.

    Args:
        env: Parsed environment key-value pairs.
        required: Keys that must be present.
        schema: Mapping of key -> type name (int, bool, url, nonempty).
        allow_unknown: When False, keys not in schema are flagged as unknown.
    """
    result = ValidationResult()

    if required:
        for key in required:
            if key not in env:
                result.missing_required.append(key)

    if schema:
        known_keys: Set[str] = set(schema.keys())

        if not allow_unknown:
            for key in env:
                if key not in known_keys:
                    result.unknown_keys.append(key)

        for key, type_name in schema.items():
            if key not in env:
                continue  # missing keys are handled by required check
            validator = _TYPE_VALIDATORS.get(type_name)
            if validator is None:
                continue
            if not validator(env[key]):
                result.type_errors[key] = (
                    f"expected type '{type_name}', got value '{env[key]}'"
                )

    return result
