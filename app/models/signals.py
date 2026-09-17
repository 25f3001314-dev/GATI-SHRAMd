"""Data contracts for the local-to-central mobility signal boundary."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class RawRecord:
    """Synthetic or source-native record held only inside a State Node."""

    source: str
    state: str
    district: str | None
    origin: str
    destination: str
    timestamp: str
    signal_type: str
    volume: int
    worker_id: str | None = None
    phone_number: str | None = None
    aadhaar_like_id: str | None = None
    name: str | None = None
    email: str | None = None
    metadata: dict[str, str] | None = None


@dataclass(frozen=True)
class SanitizedRecord:
    """State-level record after direct identifiers have been removed."""

    state: str
    origin: str
    destination: str
    district: str | None
    time_window: str
    source: str
    signal_type: str
    signal_count: int


@dataclass(frozen=True)
class CentralMobilitySignal:
    """Aggregate approved for central analytics; it has no worker fields."""

    origin: str
    destination: str
    time_window: str
    signal_count: int | float
    source_count: int
    district: str | None = None
    sources: tuple[str, ...] = ()

    _forbidden_identifiers: ClassVar[tuple[str, ...]] = (
        "worker_id",
        "phone",
        "aadhaar",
        "name",
        "email",
    )

    def __post_init__(self) -> None:
        """Reject accidental identifier-shaped route dimensions at the boundary."""
        values = (self.origin, self.destination, self.time_window, self.district or "")
        if any(identifier in value.lower() for value in values for identifier in self._forbidden_identifiers):
            raise ValueError("CentralMobilitySignal cannot contain direct identifiers")
        if self.signal_count < 0 or self.source_count < 0:
            raise ValueError("Central signal counts cannot be negative")

    @property
    def dimensions(self) -> dict[str, str]:
        """Compatibility view of aggregate dimensions only."""
        dimensions = {
            "origin": self.origin,
            "destination": self.destination,
            "time_window": self.time_window,
        }
        if self.district is not None:
            dimensions["district"] = self.district
        return dimensions


# Compatibility names retained for callers from Step 1.
RawMobilityRecord = RawRecord
SanitizedMobilitySignal = SanitizedRecord
CentralSignal = CentralMobilitySignal
