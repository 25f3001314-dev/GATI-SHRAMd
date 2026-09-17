"""Transparent factor scoring without causal inference claims."""

from dataclasses import dataclass
from typing import Iterable

from app.analytics.features import MobilityFeature


@dataclass(frozen=True)
class FactorContribution:
    """Heuristic factor contribution labeled as demo-only."""

    factor: str
    direction: str
    relative_contribution: float
    status: str = "DEMO"


def analyze_factors(features: Iterable[MobilityFeature]) -> list[FactorContribution]:
    """Score observable proxies; these are not statistically validated effects."""
    feature_list = list(features)
    if not feature_list:
        return []

    max_destination_activity = max(feature.destination_activity for feature in feature_list)
    max_signal = max(feature.signal_count for feature in feature_list)
    max_destination_activity = max(max_destination_activity, 1.0)
    max_signal = max(max_signal, 1.0)
    average_week = sum(
        feature.temporal_indicators.get("week_of_year", 0.0) for feature in feature_list
    ) / len(feature_list)

    raw_scores = {
        "rainfall_anomaly": 0.0,
        "wage_differential": 0.0,
        "employment_demand": sum(
            feature.destination_activity / max_destination_activity
            for feature in feature_list
        ) / len(feature_list),
        "seasonal_demand": min(abs(average_week - 26.0) / 26.0, 1.0),
        "construction_activity": sum(
            1.0 if "construction" in feature.time_window.lower() else 0.0
            for feature in feature_list
        ) / len(feature_list),
        "agricultural_activity": sum(
            1.0 if 1 <= feature.temporal_indicators.get("week_of_year", 0.0) <= 16 else 0.2
            for feature in feature_list
        ) / len(feature_list),
        "transport_availability": sum(
            feature.source_diversity for feature in feature_list
        ) / len(feature_list),
    }
    total = sum(raw_scores.values()) or 1.0
    return [
        FactorContribution(
            factor=factor,
            direction="positive" if score > 0 else "neutral",
            relative_contribution=round(score / total, 4),
        )
        for factor, score in raw_scores.items()
    ]
