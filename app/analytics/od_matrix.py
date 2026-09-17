"""Origin-Destination matrices built from prototype predictions."""

from collections import defaultdict
from typing import Iterable

from app.analytics.gravity import GravityPrediction


def build_od_matrix(
    predictions: Iterable[GravityPrediction],
) -> dict[str, dict[str, float]]:
    """Build an origin-to-destination matrix by summing predicted flows."""
    matrix: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for prediction in predictions:
        matrix[prediction.origin][prediction.destination] += prediction.predicted_flow
    return {
        origin: {
            destination: round(flow, 4)
            for destination, flow in destinations.items()
        }
        for origin, destinations in matrix.items()
    }


def normalize_od_matrix(
    matrix: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Normalize each origin row to shares that sum to one."""
    normalized: dict[str, dict[str, float]] = {}
    for origin, destinations in matrix.items():
        total = sum(destinations.values())
        normalized[origin] = {
            destination: round(flow / total, 4) if total else 0.0
            for destination, flow in destinations.items()
        }
    return normalized
