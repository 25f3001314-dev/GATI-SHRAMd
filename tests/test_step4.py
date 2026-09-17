from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.adapters.public_data.csv_mobility import CSVMobilityAdapter, PublicDataError
from app.adapters.public_data.nasa_power import NASAPowerRainfallAdapter
from app.adapters.public_data.world_bank import WorldBankIndicatorAdapter
from app.analytics.backtest import rolling_backtest
from app.analytics.calibration import calibrate_gravity_parameters
from app.analytics.early_warning import calculate_risk_scores
from app.analytics.features import MobilityFeature
from app.analytics.gravity import GravityPrediction
from app.analytics.validation import HistoricalObservation, calculate_metrics, evaluate_predictions
from app.config.settings import get_settings
from app.data.dataset_registry import list_datasets
from app.data.geography import Coordinate, distance_between, haversine_distance
from app.data.quality import profile_records
from app.main import app
from app.models.signals import RawRecord
from app.services.data import load_data_bundle

client = TestClient(app)


def test_public_dataset_registry_is_traceable() -> None:
    datasets = list_datasets()
    public = [dataset for dataset in datasets if dataset["status"] == "PUBLIC"]

    assert len(public) >= 3
    assert all(dataset["url"].startswith("https://") for dataset in public)
    assert all(dataset["access_date"] == "2026-09-17" for dataset in public)


def test_verified_public_adapter_urls_are_explicit() -> None:
    population = WorldBankIndicatorAdapter("SP.POP.TOTL")
    rainfall = NASAPowerRainfallAdapter(25.6, 85.0, "20200101", "20200102")

    assert population.url.startswith("https://api.worldbank.org/")
    assert "SP.POP.TOTL" in population.url
    assert rainfall.url.startswith("https://power.larc.nasa.gov/")
    assert "PRECTOTCORR" in rainfall.url


def test_public_csv_ingestion_and_malformed_rows(tmp_path: Path) -> None:
    valid_path = tmp_path / "mobility.csv"
    valid_path.write_text(
        "source,state,district,origin,destination,timestamp,signal_type,volume\n"
        "public-test,Bihar,Gaya,Bihar,Maharashtra,2025-01-01T00:00:00+00:00,observed,12\n",
        encoding="utf-8",
    )
    records = CSVMobilityAdapter(valid_path).fetch_records()
    assert len(records) == 1
    assert records[0].metadata == {
        "synthetic": "false",
        "dataset_id": "public_mobility_csv_template",
    }

    malformed_path = tmp_path / "malformed.csv"
    malformed_path.write_text(
        "source,state,district,origin,destination,timestamp,signal_type,volume\n"
        "public-test,Bihar,Gaya,Bihar,Maharashtra,not-a-date,observed,not-a-number\n",
        encoding="utf-8",
    )
    with pytest.raises(PublicDataError):
        CSVMobilityAdapter(malformed_path).fetch_records()


def test_geography_calculation_and_demo_fallback() -> None:
    first = Coordinate(25.5941, 85.1376)
    second = Coordinate(19.0760, 72.8777)

    assert haversine_distance(first, first) == 0.0
    public_distance = distance_between("Bihar", "Maharashtra", {
        "Bihar": first,
        "Maharashtra": second,
    })
    demo_distance = distance_between("Bihar", "Maharashtra")
    assert public_distance.distance_source == "PUBLIC_DATA"
    assert public_distance.distance_km > 0
    assert demo_distance.distance_source == "DEMO_PROXY"


def test_quality_report_surfaces_missing_and_duplicate_values() -> None:
    records = [
        RawRecord(
            source="public",
            state="Bihar",
            district=None,
            origin="Bihar",
            destination="Delhi",
            timestamp="2025-01-01T00:00:00+00:00",
            signal_type="observed",
            volume=4,
        )
    ]
    report = profile_records(records + records, "public-test", "2026-09-17", "public")

    assert report.row_count == 2
    assert report.duplicate_records == 1
    assert report.missing_values["district"] == 2
    assert report.date_coverage["start"] == "2025-01-01T00:00:00+00:00"


def test_validation_metrics_and_insufficient_data() -> None:
    metrics = calculate_metrics([1.0, 2.0, 4.0], [1.0, 0.0, 3.0])
    assert metrics["MAE"] == 1.0
    assert "MAPE" in metrics
    assert "R2" in metrics

    prediction = GravityPrediction("Bihar", "Delhi", "2025-W01", 10.0, "DEMO")
    observation = HistoricalObservation("Bihar", "Delhi", "2025-W01", 8.0, "test")
    result = evaluate_predictions([prediction], [observation])
    assert result.evaluation_status == "VALIDATED"
    assert result.metrics["MAE"] == 2.0
    assert evaluate_predictions([], []).evaluation_status == "INSUFFICIENT_DATA"


def test_early_warning_can_use_historical_observations() -> None:
    feature = MobilityFeature(
        origin="Bihar",
        destination="Delhi",
        time_window="2025-W02",
        signal_count=20.0,
        source_count=2,
        distance_proxy=500.0,
        origin_activity=20.0,
        destination_activity=20.0,
        temporal_indicators={"seasonal_cosine": 0.0},
        source_diversity=1.0,
        signal_strength=1.0,
    )
    scores = calculate_risk_scores(
        [feature],
        historical_observations=[
            HistoricalObservation("Bihar", "Delhi", "2025-W01", 1.0, "history")
        ],
    )

    assert "recent_flow_increase" in scores[0].drivers


def _historical_features() -> list[MobilityFeature]:
    return [
        MobilityFeature(
            origin="Bihar",
            destination="Delhi",
            time_window="2025-W01",
            signal_count=10.0,
            source_count=2,
            distance_proxy=500.0,
            origin_activity=10.0,
            destination_activity=10.0,
            temporal_indicators={"seasonal_cosine": 1.0},
            source_diversity=1.0,
            signal_strength=1.0,
        ),
        MobilityFeature(
            origin="Bihar",
            destination="Delhi",
            time_window="2025-W02",
            signal_count=12.0,
            source_count=2,
            distance_proxy=500.0,
            origin_activity=12.0,
            destination_activity=12.0,
            temporal_indicators={"seasonal_cosine": 1.0},
            source_diversity=1.0,
            signal_strength=1.0,
        ),
    ]


def test_temporal_calibration_and_backtesting() -> None:
    features = _historical_features()
    observations = [
        HistoricalObservation("Bihar", "Delhi", "2025-W01", 2.0, "historical-test"),
        HistoricalObservation("Bihar", "Delhi", "2025-W02", 3.0, "historical-test"),
    ]

    calibration = calibrate_gravity_parameters(features, observations)
    backtest = rolling_backtest(features, observations)

    assert calibration.calibration_status == "CALIBRATED"
    assert calibration.training_period == ("2025-W01",)
    assert calibration.validation_period == ("2025-W02",)
    assert backtest.evaluation_status == "VALIDATED"
    assert backtest.splits[0]["validation_period"] == "2025-W02"
    assert rolling_backtest(features[:1], observations[:1]).evaluation_status == "INSUFFICIENT_DATA"


def test_demo_public_hybrid_modes_and_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"
    monkeypatch.setenv("PUBLIC_MOBILITY_CSV_PATH", str(missing_path))
    monkeypatch.setenv("DATA_MODE", "public")
    public_fallback = load_data_bundle()
    assert public_fallback.data_mode == "public"
    assert public_fallback.fallback_used is True
    assert public_fallback.data_classification == "DEMO DATA"
    hybrid_fallback = load_data_bundle("hybrid")
    assert hybrid_fallback.data_mode == "hybrid"
    assert hybrid_fallback.fallback_used is True

    valid_path = tmp_path / "mobility.csv"
    valid_path.write_text(
        "source,state,district,origin,destination,timestamp,signal_type,volume\n"
        "public-test,Bihar,Gaya,Bihar,Delhi,2025-01-01T00:00:00+00:00,observed,12\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PUBLIC_MOBILITY_CSV_PATH", str(valid_path))
    public_bundle = load_data_bundle("public")
    assert public_bundle.fallback_used is False
    assert public_bundle.data_classification == "REAL PUBLIC DATA"

    demo_bundle = load_data_bundle("demo")
    assert demo_bundle.data_classification == "DEMO DATA"
    assert get_settings().data_mode == "public"


def test_step4_api_endpoints_report_data_status() -> None:
    for path in (
        "/api/v1/data/sources",
        "/api/v1/data/status",
        "/api/v1/analytics/validation",
        "/api/v1/analytics/backtest",
        "/api/v1/analytics/model",
        "/api/v1/analytics/data-quality",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()

    validation = client.get("/api/v1/analytics/validation").json()
    assert validation["evaluation_status"] == "INSUFFICIENT_DATA"
    assert validation["data_mode"] == "demo"
    assert client.get("/api/v1/analytics/backtest").json()["evaluation_status"] == "INSUFFICIENT_DATA"
    assert client.get("/api/v1/analytics/model").json()["status"] == "PROTOTYPE"
    assert client.get("/api/v1/analytics/data-quality").json()["data_classification"] == "DEMO DATA"
