from fastapi.testclient import TestClient

from app.analytics.causal import analyze_factors
from app.analytics.early_warning import EarlyWarningParameters, calculate_risk_scores
from app.analytics.features import MobilityFeature, build_features, demo_distance_proxy
from app.analytics.forecast import forecast_corridors
from app.analytics.gravity import GravityModel, GravityParameters, GravityPrediction
from app.analytics.od_matrix import build_od_matrix, normalize_od_matrix
from app.main import app
from app.models.signals import CentralMobilitySignal
from app.services.analytics import run_intelligence_pipeline

client = TestClient(app)


def central_signal(
    origin: str = "Bihar",
    destination: str = "Maharashtra",
    count: int | float = 100,
    source_count: int = 2,
    district: str | None = None,
) -> CentralMobilitySignal:
    return CentralMobilitySignal(
        origin=origin,
        destination=destination,
        time_window="2026-W02",
        signal_count=count,
        source_count=source_count,
        district=district,
        sources=("ONORC", "FASTag")[:source_count],
    )


def test_feature_engineering_is_deterministic_and_handles_optional_fields() -> None:
    signal = central_signal(district=None)
    first = build_features([signal])
    second = build_features([signal])

    assert first == second
    assert first[0].distance_proxy == 1400.0
    assert first[0].temporal_indicators["week_of_year"] == 2.0
    assert first[0].source_diversity == 1.0
    assert build_features([]) == []
    assert demo_distance_proxy("Unknown", "Unknown") == 1000.0


def test_gravity_model_calculation_is_deterministic_and_handles_zero_distance() -> None:
    feature = MobilityFeature(
        origin="A",
        destination="B",
        time_window="2026-W01",
        signal_count=100.0,
        source_count=2,
        distance_proxy=0.0,
        origin_activity=100.0,
        destination_activity=200.0,
        temporal_indicators={},
        source_diversity=1.0,
        signal_strength=0.5,
    )
    model = GravityModel(
        GravityParameters(alpha=1.0, gamma=1.0, beta=1.0, delta=1.0, epsilon=1.0)
    )

    first = model.predict(feature)
    second = model.predict(feature)

    assert first == second
    assert first.predicted_flow == 10000.0
    assert first.quality_flag == "DEMO_HIGH_SIGNAL_COVERAGE"


def test_gravity_handles_zero_signal_and_empty_inputs() -> None:
    features = build_features([central_signal(count=0, source_count=0)])
    predictions = GravityModel().predict_many(features)

    assert predictions[0].predicted_flow == 0.0
    assert GravityModel().predict_many([]) == []


def test_od_matrix_construction_and_normalization() -> None:
    predictions = [
        GravityPrediction("Bihar", "Maharashtra", "2026-W02", 1250.0, "DEMO"),
        GravityPrediction("Bihar", "Delhi", "2026-W02", 750.0, "DEMO"),
        GravityPrediction("Bihar", "Maharashtra", "2026-W03", 250.0, "DEMO"),
    ]

    matrix = build_od_matrix(predictions)
    normalized = normalize_od_matrix(matrix)

    assert matrix == {"Bihar": {"Maharashtra": 1500.0, "Delhi": 750.0}}
    assert normalized["Bihar"]["Maharashtra"] == 0.6667
    assert round(sum(normalized["Bihar"].values()), 4) == 1.0
    assert normalize_od_matrix({}) == {}


def test_causal_factor_output_is_demo_only() -> None:
    feature = build_features([central_signal()])
    factors = analyze_factors(feature)

    assert factors
    assert {factor.status for factor in factors} == {"DEMO"}
    assert {factor.factor for factor in factors} >= {
        "employment_demand",
        "transport_availability",
        "wage_differential",
    }
    assert analyze_factors([]) == []


def test_early_warning_thresholds_and_empty_input() -> None:
    high_feature = MobilityFeature(
        origin="A",
        destination="B",
        time_window="2026-W01",
        signal_count=100.0,
        source_count=3,
        distance_proxy=10.0,
        origin_activity=100.0,
        destination_activity=100.0,
        temporal_indicators={"seasonal_cosine": 1.0},
        source_diversity=1.0,
        signal_strength=1.0,
    )
    low_feature = MobilityFeature(
        **{**high_feature.__dict__, "signal_count": 0.0, "source_count": 0, "source_diversity": 0.0}
    )

    scores = calculate_risk_scores(
        [high_feature, low_feature],
        EarlyWarningParameters(low_threshold=0.2, medium_threshold=0.8),
    )

    assert scores[0].risk_level == "HIGH"
    assert scores[1].risk_level == "MEDIUM"
    assert calculate_risk_scores([]) == []


def test_corridor_forecast_is_a_simple_baseline() -> None:
    forecasts = forecast_corridors(
        [central_signal(count=100), central_signal(count=200)],
        forecast_window=2,
    )

    assert forecasts[0].corridor == "Bihar -> Maharashtra"
    assert forecasts[0].predicted_flow == (150.0, 150.0)
    assert forecasts[0].method == "Prototype baseline forecast"
    assert forecast_corridors([], forecast_window=2) == []


def test_complete_intelligence_pipeline() -> None:
    result = run_intelligence_pipeline()

    assert result.central_signals
    assert result.features
    assert result.gravity_predictions
    assert result.od_matrix
    assert result.normalized_od_matrix
    assert result.factors
    assert result.early_warnings
    assert result.corridor_forecasts
    assert all(prediction.quality_flag.startswith("DEMO_") for prediction in result.gravity_predictions)


def test_all_analytics_api_endpoints() -> None:
    for path in (
        "/api/v1/analytics/demo",
        "/api/v1/analytics/od-matrix",
        "/api/v1/analytics/early-warning",
        "/api/v1/analytics/corridors",
        "/api/v1/analytics/factors",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()

    demo = client.get("/api/v1/analytics/demo").json()
    assert demo["gravity_predictions"][0]["quality_flag"].startswith("DEMO_")
    assert client.get("/api/v1/analytics/od-matrix").json()["status"] == "DEMO"
    assert client.get("/api/v1/analytics/early-warning").json()["scores"]
    assert client.get("/api/v1/analytics/corridors").json()["corridors"]
    assert client.get("/api/v1/analytics/factors").json()["factors"]
