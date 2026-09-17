"""Data-mode orchestration and explicit public-to-demo fallback."""

from dataclasses import dataclass
from pathlib import Path

from app.adapters.demo_sources import DEMO_ADAPTERS
from app.adapters.public_data.csv_mobility import CSVMobilityAdapter, PublicDataError
from app.config.settings import get_settings
from app.data.dataset_registry import list_datasets
from app.data.quality import DataQualityReport, profile_records
from app.models.signals import CentralMobilitySignal, RawRecord
from app.services.pipeline import run_demo_pipeline
from app.services.state_node import StateNode

SUPPORTED_DATA_MODES = {"demo", "public", "hybrid"}


@dataclass(frozen=True)
class DataBundle:
    """Central signals plus provenance and quality facts for one run."""

    central_signals: list[CentralMobilitySignal]
    data_mode: str
    data_classification: str
    fallback_used: bool
    dataset_ids: list[str]
    quality_report: DataQualityReport
    distance_source: str = "DEMO_PROXY"


def _demo_records() -> list[RawRecord]:
    return [record for adapter_type in DEMO_ADAPTERS for record in adapter_type().fetch_records()]


def _demo_bundle(mode: str, fallback_used: bool) -> DataBundle:
    records = _demo_records()
    return DataBundle(
        central_signals=run_demo_pipeline(),
        data_mode=mode,
        data_classification="DEMO DATA",
        fallback_used=fallback_used,
        dataset_ids=["synthetic_demo_adapters"],
        quality_report=profile_records(
            records,
            source="Synthetic Step 2 adapters",
            access_date="2026-09-17",
            data_mode="demo",
        ),
    )


def _public_bundle(mode: str, path: str) -> DataBundle:
    records = CSVMobilityAdapter(path).fetch_records()
    if not records:
        raise PublicDataError("Public mobility CSV contains no records")
    state_code = records[0].state[:3].upper()
    node = StateNode(state_code)
    node.ingest(records)
    return DataBundle(
        central_signals=node.emit_central_signal(),
        data_mode=mode,
        data_classification="REAL PUBLIC DATA",
        fallback_used=False,
        dataset_ids=["public_mobility_csv_template"],
        quality_report=profile_records(
            records,
            source="Operator-supplied public mobility CSV",
            access_date="2026-09-17",
            data_mode="public",
        ),
    )


def load_data_bundle(data_mode: str | None = None) -> DataBundle:
    """Load the selected mode without hiding public-data fallback behavior."""
    settings = get_settings()
    mode = (data_mode or settings.data_mode).lower()
    if mode not in SUPPORTED_DATA_MODES:
        raise ValueError(f"Unsupported DATA_MODE: {mode}")
    if mode == "demo":
        return _demo_bundle(mode, fallback_used=False)

    try:
        return _public_bundle(mode, settings.public_mobility_csv_path)
    except (OSError, PublicDataError, ValueError):
        return _demo_bundle(mode, fallback_used=True)


def data_status(data_mode: str | None = None) -> dict[str, object]:
    """Report configured sources and local availability without network calls."""
    settings = get_settings()
    mode = (data_mode or settings.data_mode).lower()
    public_csv_available = Path(settings.public_mobility_csv_path).exists()
    datasets = list_datasets()
    for dataset in datasets:
        if dataset["dataset_id"] == "public_mobility_csv_template":
            dataset["available"] = public_csv_available
        elif dataset["status"] == "PUBLIC":
            dataset["available"] = True
            dataset["fetched"] = False
    classification = (
        "DEMO DATA"
        if mode == "demo"
        else "REAL PUBLIC DATA" if public_csv_available else "DEMO DATA"
    )
    return {
        "data_mode": mode,
        "data_classification": classification,
        "fallback_used": mode != "demo" and not public_csv_available,
        "datasets": datasets,
    }
