"""Versioned API routes for the demo pipeline."""

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.adapters.demo_sources import DEMO_ADAPTERS
from app.schemas.pipeline import (
    CentralSignalResponse,
    CorridorsResponse,
    FactorsResponse,
    FactorContributionResponse,
    IngestRequest,
    PipelineResponse,
    SourceInfo,
    StateNodeStatus,
)
from app.services.pipeline import (
    ingest_demo_sources,
    latest_state_node,
    run_demo_pipeline,
)
from app.services.analytics import run_intelligence_pipeline
from app.services.analytics import (
    data_quality,
    model_metadata,
    run_backtest,
    run_validation,
)
from app.services.data import data_status

api_router = APIRouter()


@api_router.get("/health", tags=["system"])
def versioned_health_check() -> dict[str, str]:
    """Return the versioned API liveness response."""
    return {"status": "ok", "api_version": "v1"}


@api_router.get("/sources", response_model=list[SourceInfo], tags=["demo"])
def list_sources() -> list[SourceInfo]:
    """List available synthetic adapters and their integration status."""
    return [SourceInfo(name=adapter_type.name) for adapter_type in DEMO_ADAPTERS]


@api_router.get("/signals/demo", response_model=PipelineResponse, tags=["demo"])
def demo_signals() -> PipelineResponse:
    """Run all synthetic sources through the complete State Node pipeline."""
    signals = run_demo_pipeline()
    return PipelineResponse(
        status="ok",
        state_code=latest_state_node().state_code,
        signal_count=len(signals),
        signals=[
            CentralSignalResponse(
                **{**signal.__dict__, "sources": list(signal.sources)}
            )
            for signal in signals
        ],
    )


@api_router.post("/state-node/ingest", response_model=StateNodeStatus, tags=["demo"])
def ingest_state_node(request: IngestRequest) -> StateNodeStatus:
    """Ingest synthetic records into an isolated in-memory State Node."""
    try:
        node = ingest_demo_sources(request.state_code, request.source)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return StateNodeStatus(**node.status())


@api_router.get("/state-node/status", response_model=StateNodeStatus, tags=["demo"])
def state_node_status() -> StateNodeStatus:
    """Return State Node counters without exposing raw or sanitized records."""
    return StateNodeStatus(**latest_state_node().status())


@api_router.get("/analytics/demo", tags=["analytics"])
def demo_analytics() -> dict[str, object]:
    """Run the complete synthetic predictive intelligence pipeline."""
    return run_intelligence_pipeline().to_dict()


@api_router.get("/analytics/od-matrix", tags=["analytics"])
def analytics_od_matrix() -> dict[str, object]:
    """Return prototype raw and normalized O-D matrices."""
    result = run_intelligence_pipeline()
    return {
        "status": "DEMO",
        "data_mode": result.data_mode,
        "data_classification": result.data_classification,
        "fallback_used": result.fallback_used,
        "od_matrix": result.od_matrix,
        "normalized_od_matrix": result.normalized_od_matrix,
    }


@api_router.get("/analytics/early-warning", tags=["analytics"])
def analytics_early_warning() -> dict[str, object]:
    """Return prototype early-warning scores for synthetic corridors."""
    result = run_intelligence_pipeline()
    return {
        "status": "DEMO",
        "data_mode": result.data_mode,
        "data_classification": result.data_classification,
        "fallback_used": result.fallback_used,
        "scores": result.to_dict()["early_warnings"],
    }


@api_router.get(
    "/analytics/corridors",
    response_model=CorridorsResponse,
    tags=["analytics"],
)
def analytics_corridors() -> CorridorsResponse:
    """Return transparent baseline corridor forecasts."""
    result = run_intelligence_pipeline()
    return CorridorsResponse(
        status="DEMO",
        data_mode=result.data_mode,
        data_classification=result.data_classification,
        fallback_used=result.fallback_used,
        corridors=result.to_dict()["corridor_forecasts"],
    )


@api_router.get(
    "/analytics/factors",
    response_model=FactorsResponse,
    tags=["analytics"],
)
def analytics_factors() -> FactorsResponse:
    """Return heuristic factor contributions, not causal effects."""
    result = run_intelligence_pipeline()
    return FactorsResponse(
        status="DEMO",
        data_mode=result.data_mode,
        data_classification=result.data_classification,
        fallback_used=result.fallback_used,
        factors=result.to_dict()["factors"],
    )


@api_router.get("/data/sources", tags=["data"])
def data_sources() -> dict[str, object]:
    """List registered public datasets and their provenance metadata."""
    return data_status()


@api_router.get("/data/status", tags=["data"])
def current_data_status() -> dict[str, object]:
    """Report mode, classification, and fallback state without network access."""
    return data_status()


@api_router.get("/analytics/validation", tags=["analytics"])
def analytics_validation() -> dict[str, object]:
    """Evaluate predictions against separate observed historical data if available."""
    result = run_validation()
    status = data_status()
    return {
        **asdict(result),
        "data_mode": status["data_mode"],
        "data_classification": status["data_classification"],
        "fallback_used": status["fallback_used"],
    }


@api_router.get("/analytics/backtest", tags=["analytics"])
def analytics_backtest() -> dict[str, object]:
    """Run rolling temporal validation when historical observations are available."""
    result = run_backtest()
    status = data_status()
    return {
        **result.to_dict(),
        "data_mode": status["data_mode"],
        "data_classification": status["data_classification"],
        "fallback_used": status["fallback_used"],
    }


@api_router.get("/analytics/model", tags=["analytics"])
def analytics_model() -> dict[str, object]:
    """Return model parameters and calibration provenance."""
    return model_metadata()


@api_router.get("/analytics/data-quality", tags=["data"])
def analytics_data_quality() -> dict[str, object]:
    """Return row, coverage, missing-value, duplicate, and provenance facts."""
    return data_quality()
