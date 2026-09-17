# Data boundary

`RawRecord` is state-local and may contain direct identifiers. `SanitizedRecord` contains only route, time, source, and aggregate dimensions. `CentralMobilitySignal` is the only model emitted to central analytics and contains no worker-level fields.
