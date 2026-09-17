"""Historical validation metrics with honest insufficient-data behavior."""

from dataclasses import dataclass
from math import sqrt
from typing import Iterable

from app.analytics.gravity import GravityPrediction


@dataclass(frozen=True)
class HistoricalObservation:
    """Observed corridor flow from a documented historical dataset."""

    origin: str
    destination: str
    time_window: str
    observed_flow: float
    dataset_id: str = "unknown"


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluation result with metrics populated only for matched observations."""

    evaluation_status: str
    metrics: dict[str, float]
    matched_observations: int
    dataset_ids: tuple[str, ...] = ()
    message: str = ""


def calculate_metrics(predicted: Iterable[float], observed: Iterable[float]) -> dict[str, float]:
    """Calculate MAE, RMSE, valid MAPE, and R2 where mathematically defined."""
    predicted_values = list(predicted)
    observed_values = list(observed)
    if len(predicted_values) != len(observed_values):
        raise ValueError("Predicted and observed values must have equal length")
    if not predicted_values:
        return {}
    errors = [prediction - actual for prediction, actual in zip(predicted_values, observed_values)]
    metrics = {
        "MAE": round(sum(abs(error) for error in errors) / len(errors), 4),
        "RMSE": round(sqrt(sum(error * error for error in errors) / len(errors)), 4),
    }
    non_zero_pairs = [
        (prediction, actual)
        for prediction, actual in zip(predicted_values, observed_values)
        if actual != 0
    ]
    if non_zero_pairs:
        metrics["MAPE"] = round(
            sum(abs(prediction - actual) / abs(actual) for prediction, actual in non_zero_pairs)
            / len(non_zero_pairs)
            * 100,
            4,
        )
    mean_observed = sum(observed_values) / len(observed_values)
    total_sum_squares = sum((actual - mean_observed) ** 2 for actual in observed_values)
    if len(observed_values) >= 2 and total_sum_squares > 0:
        residual_sum_squares = sum(error * error for error in errors)
        metrics["R2"] = round(1 - residual_sum_squares / total_sum_squares, 4)
    return metrics


def evaluate_predictions(
    predictions: Iterable[GravityPrediction],
    observations: Iterable[HistoricalObservation],
) -> EvaluationResult:
    """Compare predictions to matching observed route/time keys."""
    observed_by_key = {
        (observation.origin, observation.destination, observation.time_window): observation
        for observation in observations
    }
    matched = [
        (prediction, observed_by_key[key])
        for prediction in predictions
        if (key := (prediction.origin, prediction.destination, prediction.time_window))
        in observed_by_key
    ]
    if not matched:
        return EvaluationResult(
            evaluation_status="INSUFFICIENT_DATA",
            metrics={},
            matched_observations=0,
            message="No matching historical observations were supplied.",
        )
    return EvaluationResult(
        evaluation_status="VALIDATED",
        metrics=calculate_metrics(
            [prediction.predicted_flow for prediction, _ in matched],
            [observation.observed_flow for _, observation in matched],
        ),
        matched_observations=len(matched),
        dataset_ids=tuple(sorted({observation.dataset_id for _, observation in matched})),
    )
