"""Deterministic feature engineering for central mobility signals.

Geographic coordinates are not available in this prototype. The distance table
below is therefore a clearly labeled demo distance proxy, not a geographic
dataset and not a claim about precise travel distance.
"""

from dataclasses import dataclass
import math
from typing import Iterable

from app.data.geography import Coordinate, distance_between
from app.models.signals import CentralMobilitySignal

DEMO_DISTANCE_PROXY_KM: dict[tuple[str, str], float] = {
    ("Bihar", "Maharashtra"): 1_400.0,
    ("Bihar", "Delhi"): 1_000.0,
    ("Uttar Pradesh", "Maharashtra"): 1_200.0,
    ("Uttar Pradesh", "Delhi"): 500.0,
}
DEFAULT_DEMO_DISTANCE_PROXY_KM = 1_000.0


@dataclass(frozen=True)
class MobilityFeature:
    """Model-ready, non-PII features derived from one central signal."""

    origin: str
    destination: str
    time_window: str
    signal_count: float
    source_count: int
    distance_proxy: float
    origin_activity: float
    destination_activity: float
    temporal_indicators: dict[str, float]
    source_diversity: float
    signal_strength: float
    district: str | None = None
    distance_source: str = "DEMO_PROXY"


def demo_distance_proxy(origin: str, destination: str) -> float:
    """Return a documented demo distance proxy when coordinates are unavailable."""
    return DEMO_DISTANCE_PROXY_KM.get(
        (origin, destination), DEFAULT_DEMO_DISTANCE_PROXY_KM
    )


def _week_number(time_window: str) -> int:
    try:
        return int(time_window.rsplit("-W", maxsplit=1)[1])
    except (IndexError, ValueError):
        return 0


def build_features(
    signals: Iterable[CentralMobilitySignal],
    coordinates: dict[str, Coordinate] | None = None,
) -> list[MobilityFeature]:
    """Convert central signals into deterministic model features."""
    signal_list = list(signals)
    if not signal_list:
        return []

    origin_totals: dict[str, float] = {}
    destination_totals: dict[str, float] = {}
    max_signal = max((float(signal.signal_count) for signal in signal_list), default=0.0)
    max_source_count = max((signal.source_count for signal in signal_list), default=0)

    for signal in signal_list:
        origin_totals[signal.origin] = origin_totals.get(signal.origin, 0.0) + signal.signal_count
        destination_totals[signal.destination] = destination_totals.get(signal.destination, 0.0) + signal.signal_count

    features: list[MobilityFeature] = []
    for signal in signal_list:
        week = _week_number(signal.time_window)
        geographic_distance = distance_between(
            signal.origin, signal.destination, coordinates
        )
        features.append(
            MobilityFeature(
                origin=signal.origin,
                destination=signal.destination,
                time_window=signal.time_window,
                signal_count=float(signal.signal_count),
                source_count=signal.source_count,
                distance_proxy=geographic_distance.distance_km,
                origin_activity=origin_totals[signal.origin],
                destination_activity=destination_totals[signal.destination],
                temporal_indicators={
                    "week_of_year": float(week),
                    "quarter": float(math.ceil(week / 13)) if week else 0.0,
                    "seasonal_sine": math.sin(2 * math.pi * week / 52) if week else 0.0,
                    "seasonal_cosine": math.cos(2 * math.pi * week / 52) if week else 0.0,
                },
                source_diversity=(signal.source_count / max_source_count) if max_source_count else 0.0,
                signal_strength=(float(signal.signal_count) / max_signal) if max_signal else 0.0,
                district=signal.district,
                distance_source=geographic_distance.distance_source,
            )
        )
    return features
