"""Prototype privacy transformation interfaces."""

import random
from typing import Protocol

from app.models.signals import CentralMobilitySignal, SanitizedRecord


class PrivacyEngine(Protocol):
    """Contract for a reviewed privacy transformation implementation."""

    def transform(
        self, signals: list[SanitizedRecord]
    ) -> list[CentralMobilitySignal]:
        """Transform approved state aggregates for central analytics."""


class DemoPrivacyEngine:
    """Prototype privacy transformation; requires formal DP calibration and security review before production."""

    def __init__(
        self,
        min_group_size: int = 1,
        noise_enabled: bool = False,
        noise_scale: float = 0.0,
        random_seed: int = 7,
    ) -> None:
        if min_group_size < 1 or noise_scale < 0:
            raise ValueError("Privacy parameters must be positive or zero")
        self.min_group_size = min_group_size
        self.noise_enabled = noise_enabled
        self.noise_scale = noise_scale
        self._random = random.Random(random_seed)

    def transform(
        self, signals: list[SanitizedRecord]
    ) -> list[CentralMobilitySignal]:
        """Apply demo suppression and optional bounded noise, not formal DP."""
        central_signals: list[CentralMobilitySignal] = []
        for signal in signals:
            if signal.signal_count < self.min_group_size:
                continue
            count: int | float = signal.signal_count
            if self.noise_enabled and self.noise_scale:
                count = max(0, round(count + self._random.uniform(-self.noise_scale, self.noise_scale), 2))
            central_signals.append(
                CentralMobilitySignal(
                    origin=signal.origin,
                    destination=signal.destination,
                    district=signal.district,
                    time_window=signal.time_window,
                    signal_count=count,
                    source_count=1,
                    sources=(signal.source,),
                )
            )
        return central_signals


# Step 1 compatibility name. New code should use DemoPrivacyEngine.
PlaceholderPrivacyEngine = DemoPrivacyEngine
