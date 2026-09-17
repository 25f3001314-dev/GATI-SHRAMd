"""Deep Gravity Prototype.

This is a deterministic gravity-style model with multiple signal features. It
is not a trained neural network and has no measured accuracy claim.
"""

from dataclasses import dataclass
from typing import Iterable

from app.analytics.features import MobilityFeature


@dataclass(frozen=True)
class GravityParameters:
    """Prototype parameters, exposed through application configuration."""

    gravitational_constant: float = 1.0
    alpha: float = 0.8
    gamma: float = 0.9
    beta: float = 1.2
    delta: float = 0.7
    epsilon: float = 1.0


@dataclass(frozen=True)
class GravityPrediction:
    """Prototype flow estimate with a transparent quality flag."""

    origin: str
    destination: str
    time_window: str
    predicted_flow: float
    quality_flag: str
    district: str | None = None


class GravityModel:
    """Calculate deterministic gravity-style flow estimates."""

    def __init__(self, parameters: GravityParameters | None = None) -> None:
        self.parameters = parameters or GravityParameters()
        if self.parameters.epsilon <= 0:
            raise ValueError("Gravity epsilon must be greater than zero")

    def predict(self, feature: MobilityFeature) -> GravityPrediction:
        """Apply the prototype observed-signal gravity equation."""
        parameters = self.parameters
        distance = max(feature.distance_proxy, 0.0)
        predicted_flow = (
            parameters.gravitational_constant
            * feature.origin_activity**parameters.alpha
            * feature.destination_activity**parameters.gamma
            * max(feature.signal_strength, 0.0) ** parameters.delta
            / (distance + parameters.epsilon) ** parameters.beta
        )
        quality_flag = (
            "DEMO_HIGH_SIGNAL_COVERAGE"
            if feature.source_count >= 2
            else "DEMO_LOW_SIGNAL_COVERAGE"
        )
        return GravityPrediction(
            origin=feature.origin,
            destination=feature.destination,
            time_window=feature.time_window,
            predicted_flow=round(predicted_flow, 4),
            quality_flag=quality_flag,
            district=feature.district,
        )

    def predict_many(
        self, features: Iterable[MobilityFeature]
    ) -> list[GravityPrediction]:
        """Predict a stable ordered list of prototype flows."""
        return [self.predict(feature) for feature in features]
