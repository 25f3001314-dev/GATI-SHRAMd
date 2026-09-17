from app.adapters.base import DataSourceAdapter
from app.adapters.demo_sources import DEMO_ADAPTERS
from app.models.signals import RawMobilityRecord


def test_all_demo_adapters_implement_contract() -> None:
    for adapter_type in DEMO_ADAPTERS:
        adapter: DataSourceAdapter = adapter_type()
        records = adapter.fetch_records()

        assert adapter.name
        assert records
        assert all(isinstance(record, RawMobilityRecord) for record in records)


def test_state_node_does_not_forward_raw_identifiers() -> None:
    from app.services.state_node import StateNode

    node = StateNode("BR")
    node.ingest(DEMO_ADAPTERS[0]())
    signals = node.approved_central_signals()

    assert signals
    assert all("worker_id" not in signal.dimensions for signal in signals)
    assert all("phone_number" not in signal.dimensions for signal in signals)
