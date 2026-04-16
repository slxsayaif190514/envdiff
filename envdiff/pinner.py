"""Pin current env values to a lockfile for drift detection."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class PinError(Exception):
    pass


@dataclass
class PinEntry:
    key: str
    pinned_value: str
    current_value: Optional[str]

    @property
    def drifted(self) -> bool:
        return self.current_value != self.pinned_value

    def __repr__(self) -> str:
        return f"PinEntry({self.key!r}, drifted={self.drifted})"


@dataclass
class PinResult:
    filename: str
    entries: List[PinEntry] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return all(not e.drifted for e in self.entries)

    @property
    def drift_count(self) -> int:
        return sum(1 for e in self.entries if e.drifted)

    @property
    def drifted_keys(self) -> List[str]:
        return sorted(e.key for e in self.entries if e.drifted)


def save_pin(env: Dict[str, str], path: Path) -> None:
    """Write a pin lockfile from the given env dict."""
    try:
        path.write_text(json.dumps(env, sort_keys=True, indent=2))
    except OSError as exc:
        raise PinError(f"Cannot write pin file: {exc}") from exc


def load_pin(path: Path) -> Dict[str, str]:
    """Load a pin lockfile and return the dict."""
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PinError(f"Cannot read pin file: {exc}") from exc


def check_pin(pinned: Dict[str, str], current: Dict[str, str], filename: str) -> PinResult:
    """Compare pinned values against current env, return PinResult."""
    entries: List[PinEntry] = []
    all_keys = sorted(set(pinned) | set(current))
    for key in all_keys:
        if key in pinned:
            entries.append(PinEntry(key, pinned[key], current.get(key)))
    return PinResult(filename=filename, entries=entries)
