"""Transparent baseline corridor forecasting."""

from dataclasses import dataclass
from collections import defaultdict
from typing import Iterable

from app.models.signals import CentralMobilitySignal


@dataclass(frozen=True)
class CorridorForecast:
    """Moving-average baseline forecast labeled as a prototype estimate."""

    corridor: str
    forecast_horizon: str
    predicted_flow: tuple[float, ...]
    method: str = "Prototype baseline forecast"


def forecast_corridors(
    signals: Iterable[CentralMobilitySignal],
    forecast_window: int = 4,
) -> list[CorridorForecast]:
    """Forecast each corridor with a transparent moving-average baseline."""
    if forecast_window < 1:
        raise ValueError("Forecast window must be at least one")
    history: dict[tuple[str, str], list[float]] = defaultdict(list)
    for signal in signals:
        history[(signal.origin, signal.destination)].append(float(signal.signal_count))

    return [
        CorridorForecast(
            corridor=f"{origin} -> {destination}",
            forecast_horizon=f"1-{forecast_window} weeks",
            predicted_flow=tuple(
                round(sum(values[-forecast_window:]) / min(len(values), forecast_window), 4)
                for _ in range(forecast_window)
            ),
        )
        for (origin, destination), values in sorted(history.items())
    ]
