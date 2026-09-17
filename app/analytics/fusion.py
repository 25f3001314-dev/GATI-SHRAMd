"""Central signal fusion boundary.

Advanced gravity, causal, and forecasting models are intentionally deferred.
"""

from collections import defaultdict

from app.models.signals import CentralMobilitySignal


def accept_state_signals(
    signals: list[CentralMobilitySignal],
) -> list[CentralMobilitySignal]:
    """Fuse approved source signals without receiving raw worker records."""
    grouped: dict[tuple[str, str, str | None, str], list[CentralMobilitySignal]] = defaultdict(list)
    for signal in signals:
        grouped[(signal.origin, signal.destination, signal.district, signal.time_window)].append(signal)

    return [
        CentralMobilitySignal(
            origin=origin,
            destination=destination,
            district=district,
            time_window=time_window,
            signal_count=sum(signal.signal_count for signal in group),
            source_count=len({source for signal in group for source in signal.sources}),
            sources=tuple(sorted({source for signal in group for source in signal.sources})),
        )
        for (origin, destination, district, time_window), group in grouped.items()
    ]
