"""End-to-end synthetic demo pipeline orchestration."""

from app.adapters.base import DataSourceAdapter
from app.adapters.demo_sources import DEMO_ADAPTERS
from app.models.signals import CentralMobilitySignal
from app.services.state_node import StateNode

_latest_state_node: StateNode | None = None


def available_demo_adapters() -> list[DataSourceAdapter]:
    """Return fresh instances of every synthetic source adapter."""
    return [adapter_type() for adapter_type in DEMO_ADAPTERS]


def run_demo_pipeline(state_code: str = "BR") -> list[CentralMobilitySignal]:
    """Run all demo adapters through one isolated State Node."""
    global _latest_state_node
    state_node = StateNode(state_code)
    for adapter in available_demo_adapters():
        state_node.ingest(adapter)
    _latest_state_node = state_node
    return state_node.emit_central_signal()


def ingest_demo_sources(state_code: str = "BR", source: str | None = None) -> StateNode:
    """Ingest all demos or one named demo source into a fresh State Node."""
    global _latest_state_node
    state_node = StateNode(state_code)
    adapters = available_demo_adapters()
    if source is not None:
        adapters = [adapter for adapter in adapters if adapter.name == source]
        if not adapters:
            raise ValueError(f"Unknown demo source: {source}")
    for adapter in adapters:
        state_node.ingest(adapter)
    _latest_state_node = state_node
    return state_node


def latest_state_node() -> StateNode:
    """Return the latest in-memory demo State Node, creating an empty one if needed."""
    global _latest_state_node
    if _latest_state_node is None:
        _latest_state_node = StateNode("BR")
    return _latest_state_node
