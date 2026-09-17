"""Prototype Early-Warning Score."""

from dataclasses import dataclass
from typing import Iterable

from app.analytics.features import MobilityFeature
from app.analytics.validation import HistoricalObservation


@dataclass(frozen=True)
class EarlyWarningParameters:
    """Configurable thresholds for demo risk levels."""

    low_threshold: float = 0.33
    medium_threshold: float = 0.66


@dataclass(frozen=True)
class RiskScore:
    """Transparent risk score, not an operational migration warning."""

    origin: str
    destination: str
    risk_score: float
    risk_level: str
    drivers: tuple[str, ...]
    label: str = "Prototype Early-Warning Score"
    data_mode: str = "demo"
    evaluation_status: str = "DEMO_ONLY"


def calculate_risk_scores(
    features: Iterable[MobilityFeature],
    parameters: EarlyWarningParameters | None = None,
    data_mode: str = "demo",
    evaluation_status: str | None = None,
    historical_observations: Iterable[HistoricalObservation] | None = None,
) -> list[RiskScore]:
    """Calculate bounded heuristic scores from feature availability."""
    parameters = parameters or EarlyWarningParameters()
    if not 0 <= parameters.low_threshold <= parameters.medium_threshold <= 1:
        raise ValueError("Risk thresholds must be ordered between zero and one")
    feature_list = list(features)
    if not feature_list:
        return []

    max_signal = max((feature.signal_count for feature in feature_list), default=1.0) or 1.0
    max_destination_activity = max(
        (feature.destination_activity for feature in feature_list), default=1.0
    ) or 1.0
    historical_by_route: dict[tuple[str, str], list[float]] = {}
    for observation in historical_observations or []:
        historical_by_route.setdefault(
            (observation.origin, observation.destination), []
        ).append(observation.observed_flow)
    scores: list[RiskScore] = []
    resolved_evaluation_status = evaluation_status or (
        "DEMO_ONLY" if data_mode == "demo" else "INSUFFICIENT_DATA"
    )
    for feature in feature_list:
        historical_values = historical_by_route.get((feature.origin, feature.destination), [])
        if historical_values:
            comparison_baseline = sum(historical_values) / len(historical_values)
            recent_flow_increase = (
                min(
                    max(feature.signal_count - comparison_baseline, 0.0)
                    / comparison_baseline,
                    1.0,
                )
                if comparison_baseline
                else 0.0
            )
        else:
            recent_flow_increase = min(feature.signal_count / max_signal, 1.0)
        seasonal_deviation = abs(feature.temporal_indicators.get("seasonal_cosine", 0.0))
        destination_demand = min(feature.destination_activity / max_destination_activity, 1.0)
        transport_change = feature.source_diversity
        score = round(
            0.30 * recent_flow_increase
            + 0.15 * seasonal_deviation
            + 0.25 * destination_demand
            + 0.15 * transport_change
            + 0.15 * feature.source_diversity,
            4,
        )
        if score >= parameters.medium_threshold:
            level = "HIGH"
        elif score >= parameters.low_threshold:
            level = "MEDIUM"
        else:
            level = "LOW"
        drivers = tuple(
            driver
            for driver, value in (
                ("recent_flow_increase", recent_flow_increase),
                ("seasonal_deviation", seasonal_deviation),
                ("destination_demand", destination_demand),
                ("transport_signal_change", transport_change),
                ("source_diversity", feature.source_diversity),
            )
            if value >= 0.5
        )
        scores.append(
            RiskScore(
                origin=feature.origin,
                destination=feature.destination,
                risk_score=score,
                risk_level=level,
                drivers=drivers,
                data_mode=data_mode,
                evaluation_status=resolved_evaluation_status,
            )
        )
    return scores
