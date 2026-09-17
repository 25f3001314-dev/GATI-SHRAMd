"""State Node orchestration and the local privacy boundary."""

from datetime import datetime
from collections.abc import Iterable

from app.adapters.base import DataSourceAdapter
from app.models.signals import (
    CentralMobilitySignal,
    RawRecord,
    SanitizedRecord,
)
from app.analytics.fusion import accept_state_signals
from app.config.settings import get_settings
from app.privacy.engine import DemoPrivacyEngine, PrivacyEngine
from app.services.aggregation import aggregate_records


class StateNode:
    """Isolated state-level processor that never forwards raw records."""

    def __init__(
        self,
        state_code: str,
        privacy_engine: PrivacyEngine | None = None,
    ) -> None:
        self.state_code = state_code
        settings = get_settings()
        self.privacy_engine = privacy_engine or DemoPrivacyEngine(
            min_group_size=settings.privacy_min_group_size,
            noise_enabled=settings.privacy_demo_noise_enabled,
            noise_scale=settings.privacy_demo_noise_scale,
            random_seed=settings.privacy_demo_random_seed,
        )
        self._raw_records: list[RawRecord] = []
        self._validated_records: list[RawRecord] = []
        self._sanitized_records: list[SanitizedRecord] = []
        self._aggregated_records: list[SanitizedRecord] = []
        self._central_signals: list[CentralMobilitySignal] = []
        self._last_pipeline_stage = "initialized"

    def ingest(self, source: DataSourceAdapter | Iterable[RawRecord]) -> int:
        """Ingest records into this State Node and validate them locally."""
        records = source.fetch_records() if hasattr(source, "fetch_records") else list(source)
        self._raw_records.extend(records)
        self.validate()
        self._last_pipeline_stage = "ingested"
        return len(records)

    def validate(self) -> list[RawRecord]:
        """Validate raw records before any state-local transformation."""
        for record in self._raw_records:
            if not record.source or not record.state or not record.origin or not record.destination:
                raise ValueError("Raw records require source, state, origin, and destination")
            if record.volume < 1:
                raise ValueError("Raw record volume must be positive")
            try:
                datetime.fromisoformat(record.timestamp)
            except ValueError as error:
                raise ValueError(f"Invalid record timestamp: {record.timestamp}") from error
        self._validated_records = list(self._raw_records)
        self._last_pipeline_stage = "validated"
        return list(self._validated_records)

    def sanitize(self) -> list[SanitizedRecord]:
        """Remove direct identifiers and retain only aggregate dimensions."""
        self.validate()
        self._sanitized_records = [
            SanitizedRecord(
                state=record.state,
                origin=record.origin,
                destination=record.destination,
                district=record.district,
                time_window=self._time_window(record.timestamp),
                source=record.source,
                signal_type=record.signal_type,
                signal_count=record.volume,
            )
            for record in self._validated_records
        ]
        self._last_pipeline_stage = "sanitized"
        return list(self._sanitized_records)

    def aggregate(self) -> list[SanitizedRecord]:
        """Aggregate sanitized records by route, district, window, and source."""
        self._aggregated_records = aggregate_records(self.sanitize())
        self._last_pipeline_stage = "aggregated"
        return list(self._aggregated_records)

    def privacy_transform(self) -> list[CentralMobilitySignal]:
        """Apply the configured prototype privacy transformation locally."""
        self._central_signals = self.privacy_engine.transform(self.aggregate())
        self._last_pipeline_stage = "privacy_transformed"
        return list(self._central_signals)

    def emit_central_signal(self) -> list[CentralMobilitySignal]:
        """Emit only fused aggregate signals to the central analytics boundary."""
        signals = accept_state_signals(self.privacy_transform())
        self._central_signals = signals
        self._last_pipeline_stage = "central_signal_emitted"
        return list(signals)

    def approved_central_signals(self) -> list[CentralMobilitySignal]:
        """Compatibility alias for the complete State Node pipeline."""
        return self.emit_central_signal()

    def status(self) -> dict[str, int | str]:
        """Return operational counters without returning raw records."""
        return {
            "state_code": self.state_code,
            "raw_record_count": len(self._raw_records),
            "validated_record_count": len(self._validated_records),
            "sanitized_record_count": len(self._sanitized_records),
            "aggregated_record_count": len(self._aggregated_records),
            "central_signal_count": len(self._central_signals),
            "last_pipeline_stage": self._last_pipeline_stage,
        }

    @staticmethod
    def _time_window(timestamp: str) -> str:
        parsed = datetime.fromisoformat(timestamp)
        week = parsed.isocalendar()
        return f"{week.year}-W{week.week:02d}"
