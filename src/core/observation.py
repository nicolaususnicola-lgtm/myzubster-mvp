"""Observation domain model for the MyZubster MVP."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib


@dataclass
class Observation:
    description: str
    latitude: float
    longitude: float
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    media_hash: str = ""

    def generate_id(self):
        """Generate a deterministic identifier for this observation."""
        data = f"{self.description}|{self.latitude}|{self.longitude}|{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self):
        """Return a JSON-serializable representation."""
        return {
            "id": self.generate_id(),
            "description": self.description,
            "coordinates": {"lat": self.latitude, "lng": self.longitude},
            "timestamp": self.timestamp.isoformat(),
            "media_hash": self.media_hash,
        }
