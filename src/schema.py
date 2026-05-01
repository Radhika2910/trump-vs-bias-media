from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Record:
    source_type: str
    source_name: str
    title: str
    text: str
    url: str = ""
    author: str = ""
    published_at: str = ""
    query: str = ""
    country: str = ""
    engagement: float = 0.0
    claim: str = ""
    verdict: str = ""
    media_bias: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROJECT_QUERIES = [
    '"Donald Trump" media bias',
    '"Trump" "fake news"',
    '"Trump" mainstream media',
    '"Trump" media coverage',
]

