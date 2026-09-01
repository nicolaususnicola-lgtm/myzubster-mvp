"""
Modulo per gestire osservazioni - MyZubster MVP v0.1
"""
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class Observation:
    description: str
    latitude: float
    longitude: float
    timestamp: datetime = datetime.now()
    media_hash: str = ""

    def generate_id(self):
        """Genera un ID univoco per l'osservazione"""
        data = f"{self.description}|{self.latitude}|{self.longitude}|{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self):
        """Converti l'osservazione in dizionario per JSON"""
        return {
            "id": self.generate_id(),
            "description": self.description,
            "coordinates": {"lat": self.latitude, "lng": self.longitude},
            "timestamp": self.timestamp.isoformat(),
            "media_hash": self.media_hash
        }