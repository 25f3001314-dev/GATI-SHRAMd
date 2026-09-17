"""HTTP schemas for the demo pipeline."""

from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Optional source selector for demo State Node ingestion."""

    state_code: str = Field(default="BR", min_length=2, max_length=3)
    source: str | None = None


class SourceInfo(BaseModel):
    name: str
    demo: bool = True
    integration_status: str = "synthetic demo"


class StateNodeStatus(BaseModel):
    state_code: str
    raw_record_count: int
    validated_record_count: int
    sanitized_record_count: int
    aggregated_record_count: int
    central_signal_count: int
    last_pipeline_stage: str


class CentralSignalResponse(BaseModel):
    origin: str
    destination: str
    district: str | None
    time_window: str
    signal_count: int | float
    source_count: int
    sources: list[str]


class PipelineResponse(BaseModel):
    status: str
    state_code: str
    signal_count: int
    signals: list[CentralSignalResponse]


class CorridorForecastResponse(BaseModel):
    """Prototype baseline forecast for one origin-destination corridor."""

    corridor: str
    forecast_horizon: str
    predicted_flow: list[float]
    method: str


class CorridorsResponse(BaseModel):
    """Typed response envelope for corridor forecasts."""

    status: str
    data_mode: str
    data_classification: str
    fallback_used: bool
    corridors: list[CorridorForecastResponse]


class FactorContributionResponse(BaseModel):
    """Demo factor association, not a validated causal effect."""

    factor: str
    direction: str
    relative_contribution: float
    status: str


class FactorsResponse(BaseModel):
    """Typed response envelope for prototype factor contributions."""

    status: str
    data_mode: str
    data_classification: str
    fallback_used: bool
    factors: list[FactorContributionResponse]
