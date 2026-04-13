"""Parser for .env files."""

from pathlib import Path
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when a .env file cannot be parsed."""
    pass


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key-value pairs.

    Handles:
    - KEY=VALUE
    - KEY="VALUE" or KEY='VALUE'
    - Comments (#)
    - Empty lines
    - Keys with no value (KEY=)
    """
    path = Path(filepath)
    if not path.exists():
        raise EnvParseError(f"File not found: {filepath}")
    if not path.is_file():
        raise EnvParseError(f"Not a file: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()

            # skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise EnvParseError(
                    f"Invalid syntax at line {lineno}: '{line}'"
                )

            key, _, raw_value = line.partition("=")
            key = key.strip()

            if not key:
                raise EnvParseError(
                    f"Empty key at line {lineno}: '{line}'"
                )

            value: Optional[str] = raw_value.strip()

            # strip surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[0] == value[-1]:
                value = value[1:-1]
            elif value == "":
                value = None

            env_vars[key] = value

    return env_vars
