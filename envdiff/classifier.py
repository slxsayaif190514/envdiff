"""Classify env keys by inferred category based on naming patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
import re

CATEGORY_PATTERNS: List[tuple[str, str]] = [
    ("database", r"(DB|DATABASE|POSTGRES|MYSQL|MONGO|REDIS|SQL)"),
    ("auth", r"(SECRET|TOKEN|API_KEY|AUTH|JWT|PASSWORD|PASSWD|CREDENTIAL)"),
    ("network", r"(HOST|PORT|URL|URI|ENDPOINT|DOMAIN|BASE_URL)"),
    ("logging", r"(LOG|LOGGING|SENTRY|DATADOG|NEWRELIC)"),
    ("feature", r"(FEATURE|FLAG|ENABLE|DISABLE|TOGGLE)"),
    ("storage", r"(S3|BUCKET|STORAGE|GCS|BLOB|MINIO)"),
    ("email", r"(MAIL|EMAIL|SMTP|SENDGRID|MAILGUN)"),
]

UNCATEGORIZED = "uncategorized"


@dataclass
class ClassifyResult:
    filename: str
    categories: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def category_count(self) -> int:
        return len(self.categories)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.categories.values())

    def keys_in(self, category: str) -> List[str]:
        return self.categories.get(category, [])


def _infer_category(key: str) -> str:
    upper = key.upper()
    for category, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, upper):
            return category
    return UNCATEGORIZED


def classify_env(env: Dict[str, str], filename: str = "") -> ClassifyResult:
    result = ClassifyResult(filename=filename)
    for key in sorted(env.keys()):
        cat = _infer_category(key)
        result.categories.setdefault(cat, []).append(key)
    return result
