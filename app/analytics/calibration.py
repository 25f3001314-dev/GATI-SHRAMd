"""Transparent temporal calibration for the Gravity Prototype."""

from dataclasses import asdict, dataclass
from itertools import product
from typing import Iterable

from app.analytics.features import MobilityFeature
from app.analytics.gravity import GravityModel, GravityParameters
from app.analytics.validation import HistoricalObservation, calculate_metrics


@dataclass(frozen=True)
class CalibrationResult:
    """Calibration provenance and parameters."""

    calibration_status: str
    baseline_parameters: dict[str, float]
    calibrated_parameters: dict[str, float]
    training_period: tuple[str, ...]
    validation_period: tuple[str, ...]
    dataset_ids: tuple[str, ...]
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _parameter_dict(parameters: GravityParameters) -> dict[str, float]:
    return {
        "alpha": parameters.alpha,
        "gamma": parameters.gamma,
        "beta": parameters.beta,
        "delta": parameters.delta,
    }


def calibrate_gravity_parameters(
    features: Iterable[MobilityFeature],
    observations: Iterable[HistoricalObservation],
    baseline: GravityParameters | None = None,
) -> CalibrationResult:
    """Select parameters by training-period MAE using a small transparent grid."""
    baseline = baseline or GravityParameters()
    feature_list = list(features)
    observation_list = list(observations)
    periods = sorted({observation.time_window for observation in observation_list})
    baseline_dict = _parameter_dict(baseline)
    if not feature_list or not observation_list or len(periods) < 2:
        return CalibrationResult(
            calibration_status="INSUFFICIENT_DATA",
            baseline_parameters=baseline_dict,
            calibrated_parameters=baseline_dict,
            training_period=tuple(periods[:-1]),
            validation_period=tuple(periods[-1:]),
            dataset_ids=tuple(sorted({observation.dataset_id for observation in observation_list})),
            message="At least two temporal periods are required for calibration.",
        )

    training_periods = tuple(periods[:-1])
    training_observations = [
        observation for observation in observation_list if observation.time_window in training_periods
    ]
    training_features = [feature for feature in feature_list if feature.time_window in training_periods]
    observed_by_key = {
        (observation.origin, observation.destination, observation.time_window): observation.observed_flow
        for observation in training_observations
    }
    candidates = product(
        (baseline.alpha * 0.8, baseline.alpha, baseline.alpha * 1.2),
        (baseline.gamma * 0.8, baseline.gamma, baseline.gamma * 1.2),
        (baseline.beta * 0.8, baseline.beta, baseline.beta * 1.2),
        (baseline.delta * 0.8, baseline.delta, baseline.delta * 1.2),
    )
    best_parameters = baseline
    best_mae = float("inf")
    for alpha, gamma, beta, delta in candidates:
        parameters = GravityParameters(
            gravitational_constant=baseline.gravitational_constant,
            alpha=alpha,
            gamma=gamma,
            beta=beta,
            delta=delta,
            epsilon=baseline.epsilon,
        )
        predictions = GravityModel(parameters).predict_many(training_features)
        pairs = [
            (prediction.predicted_flow, observed_by_key[key])
            for prediction in predictions
            if (key := (prediction.origin, prediction.destination, prediction.time_window))
            in observed_by_key
        ]
        if pairs:
            mae = calculate_metrics(
                [pair[0] for pair in pairs], [pair[1] for pair in pairs]
            )["MAE"]
            if mae < best_mae:
                best_mae = mae
                best_parameters = parameters
    return CalibrationResult(
        calibration_status="CALIBRATED" if best_mae < float("inf") else "INSUFFICIENT_DATA",
        baseline_parameters=baseline_dict,
        calibrated_parameters=_parameter_dict(best_parameters),
        training_period=training_periods,
        validation_period=(periods[-1],),
        dataset_ids=tuple(sorted({observation.dataset_id for observation in observation_list})),
        message="Grid-search calibration on historical training periods.",
    )
