from fastapi.testclient import TestClient

from app.adapters.demo_sources import DEMO_ADAPTERS
from app.main import app
from app.models.signals import RawRecord
from app.privacy.engine import DemoPrivacyEngine
from app.services.pipeline import run_demo_pipeline
from app.services.state_node import StateNode

client = TestClient(app)


PII_FIELDS = {"worker_id", "phone_number", "aadhaar_like_id", "name", "email"}


def test_every_demo_adapter_returns_structured_synthetic_records() -> None:
    for adapter_type in DEMO_ADAPTERS:
        records = adapter_type().fetch_records()
        assert len(records) >= 2
        for record in records:
            assert record.source == adapter_type.name
            assert record.state == "Bihar"
            assert record.origin and record.destination
            assert record.timestamp and record.signal_type
            assert record.volume > 0
            assert record.metadata == {"synthetic": "true", "adapter": adapter_type.name}


def test_state_node_accepts_and_validates_records() -> None:
    node = StateNode("BR")
    count = node.ingest(DEMO_ADAPTERS[0]())

    assert count == 2
    assert node.status()["validated_record_count"] == 2


def test_sanitization_removes_all_direct_identifiers() -> None:
    node = StateNode("BR")
    node.ingest(
        [
            RawRecord(
                source="synthetic-test",
                state="Bihar",
                district="Gaya",
                origin="Bihar",
                destination="Maharashtra",
                timestamp="2026-01-05T00:00:00+00:00",
                signal_type="test",
                volume=12,
                worker_id="worker-secret",
                phone_number="+91-9999999999",
                aadhaar_like_id="1234-5678-9012",
                name="Private Name",
                email="private@example.invalid",
            )
        ]
    )

    sanitized = node.sanitize()
    central = node.emit_central_signal()

    assert sanitized
    assert not any(hasattr(record, field) for record in sanitized for field in PII_FIELDS)
    assert central
    assert not any(field in repr(signal).lower() for signal in central for field in PII_FIELDS)


def test_aggregation_produces_route_and_source_counts() -> None:
    node = StateNode("BR")
    node.ingest(DEMO_ADAPTERS[0]())
    node.ingest(DEMO_ADAPTERS[1]())
    signals = node.emit_central_signal()

    route_signal = next(signal for signal in signals if signal.destination == "Maharashtra")
    assert route_signal.origin == "Bihar"
    assert route_signal.time_window == "2026-W02"
    assert route_signal.signal_count > 0
    assert route_signal.source_count == 2
    assert set(route_signal.sources) == {"ONORC", "Indian Railways UTS"}


def test_demo_privacy_transformation_runs_with_configured_noise() -> None:
    node = StateNode(
        "BR",
        privacy_engine=DemoPrivacyEngine(
            min_group_size=1,
            noise_enabled=True,
            noise_scale=2.0,
            random_seed=1,
        ),
    )
    node.ingest(DEMO_ADAPTERS[0]())
    signals = node.privacy_transform()

    assert signals
    assert all(signal.signal_count >= 0 for signal in signals)


def test_complete_demo_pipeline_runs_end_to_end() -> None:
    signals = run_demo_pipeline()

    assert len(signals) >= 2
    assert all(signal.origin and signal.destination for signal in signals)
    assert all(signal.source_count >= 1 for signal in signals)
    assert not any(field in repr(signal).lower() for signal in signals for field in PII_FIELDS)


def test_pipeline_api_endpoints() -> None:
    assert client.get("/api/v1/sources").status_code == 200

    demo_response = client.get("/api/v1/signals/demo")
    assert demo_response.status_code == 200
    assert demo_response.json()["signal_count"] >= 2
    assert demo_response.json()["signals"][0]["time_window"] == "2026-W02"

    ingest_response = client.post(
        "/api/v1/state-node/ingest",
        json={"state_code": "BR", "source": "ONORC"},
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["raw_record_count"] == 2
    assert ingest_response.json()["central_signal_count"] == 0

    status_response = client.get("/api/v1/state-node/status")
    assert status_response.status_code == 200
    assert status_response.json()["state_code"] == "BR"


def test_unknown_source_returns_not_found() -> None:
    response = client.post(
        "/api/v1/state-node/ingest",
        json={"source": "not-a-real-demo-source"},
    )

    assert response.status_code == 404
