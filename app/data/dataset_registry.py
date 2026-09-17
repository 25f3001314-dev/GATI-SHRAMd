"""Traceable metadata for public and mock datasets used by the prototype."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DatasetMetadata:
    """Provenance metadata required before a dataset enters the pipeline."""

    dataset_id: str
    name: str
    source: str
    url: str
    access_type: str
    license: str
    geography: str
    time_granularity: str
    status: str
    access_date: str = "2026-09-17"


PUBLIC_DATASETS: tuple[DatasetMetadata, ...] = (
    DatasetMetadata(
        dataset_id="world_bank_india_population",
        name="World Development Indicators: Population, total",
        source="World Bank Open Data",
        url="https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL?format=json",
        access_type="API",
        license="World Bank Open Data terms; verify current terms before redistribution",
        geography="national",
        time_granularity="annual",
        status="PUBLIC",
    ),
    DatasetMetadata(
        dataset_id="world_bank_india_employment",
        name="World Development Indicators: Employment to population ratio",
        source="World Bank Open Data",
        url="https://api.worldbank.org/v2/country/IND/indicator/SL.EMP.TOTL.SP.ZS?format=json",
        access_type="API",
        license="World Bank Open Data terms; verify current terms before redistribution",
        geography="national",
        time_granularity="annual",
        status="PUBLIC",
    ),
    DatasetMetadata(
        dataset_id="nasa_power_india_rainfall",
        name="NASA POWER Daily Precipitation Corrected",
        source="NASA POWER",
        url="https://power.larc.nasa.gov/api/temporal/daily/point",
        access_type="JSON",
        license="NASA POWER data access terms; verify current terms before redistribution",
        geography="district",
        time_granularity="daily",
        status="PUBLIC",
    ),
    DatasetMetadata(
        dataset_id="public_mobility_csv_template",
        name="User-supplied public mobility observation CSV",
        source="Local file supplied by the operator",
        url="",
        access_type="CSV",
        license="Operator must record the source dataset license before use",
        geography="district",
        time_granularity="weekly or daily",
        status="MOCK",
    ),
    DatasetMetadata(
        dataset_id="public_geography_csv_template",
        name="User-supplied public place-coordinate CSV",
        source="Local file supplied by the operator",
        url="",
        access_type="CSV",
        license="Operator must record the source dataset license before use",
        geography="district",
        time_granularity="static",
        status="MOCK",
    ),
    DatasetMetadata(
        dataset_id="public_transport_csv_template",
        name="User-supplied public transport activity CSV",
        source="Local file supplied by the operator",
        url="",
        access_type="CSV",
        license="Operator must record the source dataset license before use",
        geography="district",
        time_granularity="daily or weekly",
        status="MOCK",
    ),
)


def list_datasets() -> list[dict[str, object]]:
    """Return registry metadata without attempting network access."""
    return [asdict(dataset) for dataset in PUBLIC_DATASETS]


def get_dataset(dataset_id: str) -> DatasetMetadata:
    """Return one registered dataset or raise a clear error."""
    for dataset in PUBLIC_DATASETS:
        if dataset.dataset_id == dataset_id:
            return dataset
    raise KeyError(f"Unknown dataset: {dataset_id}")
