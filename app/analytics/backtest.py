"""Rolling temporal backtesting for the Gravity Prototype."""

from dataclasses import asdict, dataclass
from typing import Iterable

from app.analytics.calibration import calibrate_gravity_parameters
from app.analytics.features import MobilityFeature
from app.analytics.gravity import GravityModel, GravityParameters
from app.analytics.validation import HistoricalObservation, calculate_metrics


@dataclass(frozen=True)
class BacktestResult:
    """Temporal backtest output with one record per validation split."""

    model: str
    evaluation_status: str
    metrics: dict[str, float]
    splits: list[dict[str, object]]
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def rolling_backtest(
    features: Iterable[MobilityFeature],
    observations: Iterable[HistoricalObservation],
    baseline: GravityParameters | None = None,
) -> BacktestResult:
    """Train on earlier periods and validate only on the next period."""
    feature_list = list(features)
    observation_list = list(observations)
    periods = sorted({observation.time_window for observation in observation_list})
    if len(periods) < 2:
        return BacktestResult(
            model="Deep Gravity Prototype",
            evaluation_status="INSUFFICIENT_DATA",
            metrics={},
            splits=[],
            message="At least two historical periods are required for backtesting.",
        )

    split_results: list[dict[str, object]] = []
    all_predictions: list[float] = []
    all_observed: list[float] = []
    for index in range(1, len(periods)):
        training_periods = periods[:index]
        validation_period = periods[index]
        training_observations = [
            observation for observation in observation_list if observation.time_window in training_periods
        ]
        validation_observations = [
            observation for observation in observation_list if observation.time_window == validation_period
        ]
        calibration = calibrate_gravity_parameters(feature_list, training_observations, baseline)
        parameters = GravityParameters(**{
            **(baseline.__dict__ if baseline else GravityParameters().__dict__),
            **calibration.calibrated_parameters,
        })
        validation_features = [
            feature for feature in feature_list if feature.time_window == validation_period
        ]
        predictions = GravityModel(parameters).predict_many(validation_features)
        observed_by_key = {
            (observation.origin, observation.destination, observation.time_window): observation.observed_flow
            for observation in validation_observations
        }
        pairs = [
            (prediction.predicted_flow, observed_by_key[key])
            for prediction in predictions
            if (key := (prediction.origin, prediction.destination, prediction.time_window))
            in observed_by_key
        ]
        if pairs:
            predicted_values = [pair[0] for pair in pairs]
            observed_values = [pair[1] for pair in pairs]
            split_results.append(
                {
                    "training_periods": training_periods,
                    "validation_period": validation_period,
                    "metrics": calculate_metrics(predicted_values, observed_values),
                }
            )
            all_predictions.extend(predicted_values)
            all_observed.extend(observed_values)

    if not all_predictions:
        return BacktestResult(
            model="Deep Gravity Prototype",
            evaluation_status="INSUFFICIENT_DATA",
            metrics={},
            splits=split_results,
            message="No validation split had matching observed flows.",
        )
    return BacktestResult(
        model="Deep Gravity Prototype",
        evaluation_status="VALIDATED",
        metrics=calculate_metrics(all_predictions, all_observed),
        splits=split_results,
    )
