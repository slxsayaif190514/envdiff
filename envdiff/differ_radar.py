"""Radar-style multi-axis comparison of two env files."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List

AXES = [
    "completeness",
    "consistency",
    "security",
    "type_alignment",
    "naming",
]


@dataclass
class RadarAxis:
    name: str
    score_a: float  # 0.0 – 1.0
    score_b: float

    @property
    def delta(self) -> float:
        return round(self.score_b - self.score_a, 4)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RadarAxis({self.name}, a={self.score_a}, b={self.score_b})"


@dataclass
class RadarResult:
    file_a: str
    file_b: str
    axes: List[RadarAxis] = field(default_factory=list)

    @property
    def overall_a(self) -> float:
        if not self.axes:
            return 1.0
        return round(sum(ax.score_a for ax in self.axes) / len(self.axes), 4)

    @property
    def overall_b(self) -> float:
        if not self.axes:
            return 1.0
        return round(sum(ax.score_b for ax in self.axes) / len(self.axes), 4)

    def get(self, name: str) -> RadarAxis | None:
        return next((ax for ax in self.axes if ax.name == name), None)


def _score_completeness(env_a: dict, env_b: dict) -> tuple[float, float]:
    all_keys = set(env_a) | set(env_b)
    if not all_keys:
        return 1.0, 1.0
    sa = len(set(env_a) & all_keys) / len(all_keys)
    sb = len(set(env_b) & all_keys) / len(all_keys)
    return round(sa, 4), round(sb, 4)


def _score_consistency(env_a: dict, env_b: dict) -> tuple[float, float]:
    shared = set(env_a) & set(env_b)
    if not shared:
        return 1.0, 1.0
    matches = sum(1 for k in shared if env_a[k] == env_b[k])
    ratio = matches / len(shared)
    return round(ratio, 4), round(ratio, 4)


def _score_security(env: dict) -> float:
    sensitive = {"password", "secret", "token", "key", "api"}
    flagged = [k for k in env if any(s in k.lower() for s in sensitive)]
    exposed = sum(1 for k in flagged if env[k] not in ("", "***", "<redacted>"))
    if not flagged:
        return 1.0
    return round(1.0 - exposed / len(flagged), 4)


def _score_type_alignment(env_a: dict, env_b: dict) -> tuple[float, float]:
    shared = set(env_a) & set(env_b)
    if not shared:
        return 1.0, 1.0

    def _type(v: str) -> str:
        if v.lower() in ("true", "false"):
            return "bool"
        try:
            int(v); return "int"
        except ValueError:
            pass
        try:
            float(v); return "float"
        except ValueError:
            pass
        return "str"

    aligned = sum(1 for k in shared if _type(env_a[k]) == _type(env_b[k]))
    ratio = aligned / len(shared)
    return round(ratio, 4), round(ratio, 4)


def _score_naming(env: dict) -> float:
    if not env:
        return 1.0
    upper = sum(1 for k in env if k == k.upper())
    return round(upper / len(env), 4)


def build_radar(file_a: str, env_a: dict, file_b: str, env_b: dict) -> RadarResult:
    result = RadarResult(file_a=file_a, file_b=file_b)

    sa, sb = _score_completeness(env_a, env_b)
    result.axes.append(RadarAxis("completeness", sa, sb))

    ca, cb = _score_consistency(env_a, env_b)
    result.axes.append(RadarAxis("consistency", ca, cb))

    result.axes.append(RadarAxis("security", _score_security(env_a), _score_security(env_b)))

    ta, tb = _score_type_alignment(env_a, env_b)
    result.axes.append(RadarAxis("type_alignment", ta, tb))

    result.axes.append(RadarAxis("naming", _score_naming(env_a), _score_naming(env_b)))

    return result
