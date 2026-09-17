"""Orchestration for the Step 3 predictive intelligence demo."""

from dataclasses import asdict, dataclass
from pathlib import Path

from app.analytics.causal import FactorContribution, analyze_factors
from app.analytics.early_warning import EarlyWarningParameters, RiskScore, calculate_risk_scores
from app.analytics.features import MobilityFeature, build_features
from app.analytics.forecast import CorridorForecast, forecast_corridors
from app.analytics.gravity import GravityModel, GravityParameters, GravityPrediction
from app.analytics.od_matrix import build_od_matrix, normalize_od_matrix
from app.analytics.backtest import BacktestResult, rolling_backtest
from app.analytics.calibration import CalibrationResult, calibrate_gravity_parameters
from app.analytics.validation import EvaluationResult, evaluate_predictions
from app.config.settings import get_settings
from app.data.historical import HistoricalDataError, load_observations
from app.data.geography import load_coordinates
from app.models.signals import CentralMobilitySignal
from app.services.data import DataBundle, load_data_bundle


@dataclass(frozen=True)
class IntelligenceResult:
    """Structured output of the synthetic intelligence pipeline."""

    central_signals: list[CentralMobilitySignal]
    features: list[MobilityFeature]
    gravity_predictions: list[GravityPrediction]
    od_matrix: dict[str, dict[str, float]]
    normalized_od_matrix: dict[str, dict[str, float]]
    factors: list[FactorContribution]
    early_warnings: list[RiskScore]
    corridor_forecasts: list[CorridorForecast]
    data_mode: str
    data_classification: str
    fallback_used: bool
    dataset_ids: list[str]
    distance_source: str
    evaluation_status: str
    data_quality: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        """Convert nested dataclasses to a JSON-serializable structure."""
        return asdict(self)


def run_intelligence_pipeline(data_mode: str | None = None) -> IntelligenceResult:
    """Run the intelligence layer on the selected public/demo data bundle."""
    settings = get_settings()
    bundle: DataBundle = load_data_bundle(data_mode)
    coordinates = None
    distance_source = "DEMO_PROXY"
    if Path(settings.public_geography_csv_path).exists():
        coordinates = load_coordinates(settings.public_geography_csv_path)
        distance_source = "PUBLIC_DATA"
    central_signals = bundle.central_signals
    features = build_features(central_signals, coordinates)
    gravity_model = GravityModel(
        GravityParameters(
            alpha=settings.gravity_alpha,
            gamma=settings.gravity_gamma,
            beta=settings.gravity_beta,
            delta=settings.gravity_delta,
            epsilon=settings.gravity_epsilon,
        )
    )
    gravity_predictions = gravity_model.predict_many(features)
    od_matrix = build_od_matrix(gravity_predictions)
    return IntelligenceResult(
        central_signals=central_signals,
        features=features,
        gravity_predictions=gravity_predictions,
        od_matrix=od_matrix,
        normalized_od_matrix=normalize_od_matrix(od_matrix),
        factors=analyze_factors(features),
        early_warnings=calculate_risk_scores(
            features,
            EarlyWarningParameters(
                low_threshold=settings.early_warning_low_threshold,
                medium_threshold=settings.early_warning_medium_threshold,
            ),
            data_mode=bundle.data_mode,
            evaluation_status=(
                "DEMO_ONLY" if bundle.data_classification == "DEMO DATA" else "INSUFFICIENT_DATA"
            ),
            historical_observations=_historical_observations(),
        ),
        corridor_forecasts=forecast_corridors(
            central_signals, settings.forecast_window
        ),
        data_mode=bundle.data_mode,
        data_classification=bundle.data_classification,
        fallback_used=bundle.fallback_used,
        dataset_ids=bundle.dataset_ids,
        distance_source=distance_source,
        evaluation_status=(
            "DEMO_ONLY" if bundle.data_classification == "DEMO DATA" else "INSUFFICIENT_DATA"
        ),
        data_quality=bundle.quality_report.to_dict(),
    )


def _historical_observations() -> list:
    """Load only operator-supplied observed flows, if available."""
    settings = get_settings()
    try:
        return load_observations(
            settings.public_historical_csv_path,
            dataset_id="public_historical_observations",
        )
    except (HistoricalDataError, OSError):
        return []


def run_validation(data_mode: str | None = None) -> EvaluationResult:
    """Evaluate against separate observed data, never against generated output."""
    result = run_intelligence_pipeline(data_mode)
    return evaluate_predictions(result.gravity_predictions, _historical_observations())


def run_backtest(data_mode: str | None = None) -> BacktestResult:
    """Run rolling temporal backtesting when historical data is present."""
    result = run_intelligence_pipeline(data_mode)
    return rolling_backtest(result.features, _historical_observations())


def model_metadata(data_mode: str | None = None) -> dict[str, object]:
    """Return baseline/calibration provenance without claiming model performance."""
    settings = get_settings()
    result = run_intelligence_pipeline(data_mode)
    observations = _historical_observations()
    calibration: CalibrationResult = calibrate_gravity_parameters(
        result.features,
        observations,
    )
    return {
        "model": "Deep Gravity Prototype",
        "status": "PROTOTYPE",
        "data_mode": result.data_mode,
        "data_classification": result.data_classification,
        "fallback_used": result.fallback_used,
        "baseline_parameters": {
            "alpha": settings.gravity_alpha,
            "gamma": settings.gravity_gamma,
            "beta": settings.gravity_beta,
            "delta": settings.gravity_delta,
            "epsilon": settings.gravity_epsilon,
        },
        "calibration": calibration.to_dict(),
        "training_period": calibration.training_period,
        "validation_period": calibration.validation_period,
        "dataset_ids": calibration.dataset_ids,
    }


def data_quality(data_mode: str | None = None) -> dict[str, object]:
    """Return quality facts and provenance for the selected data bundle."""
    bundle = load_data_bundle(data_mode)
    return {
        "data_mode": bundle.data_mode,
        "data_classification": bundle.data_classification,
        "fallback_used": bundle.fallback_used,
        "dataset_ids": bundle.dataset_ids,
        "distance_source": bundle.distance_source,
        "report": bundle.quality_report.to_dict(),
    }
