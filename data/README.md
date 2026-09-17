# Public data workflow

Large or licensed datasets are intentionally not committed to Git.

## Mobility CSV

1. Obtain a public mobility observation file and record its official source URL, license, and access date in `app/data/dataset_registry.py`.
2. Place a CSV at `data/raw/mobility.csv` with these columns:

```text
source,state,district,origin,destination,timestamp,signal_type,volume
```

3. Set `DATA_MODE=public` or `DATA_MODE=hybrid` in `.env`.
4. Run the API or process the file with:

```bash
python -m app.data.ingest --input data/raw/mobility.csv --output data/processed/mobility.json
```

5. Re-run validation and backtesting through the API after the file is available.

## Historical observations

For validation, place a separate observed-flow file at
`data/raw/historical_observations.csv` with:

```text
origin,destination,time_window,observed_flow
```

This must be a documented historical dataset, not the model's own predictions.
The service uses earlier periods for calibration and later periods for temporal
validation. Without this file, validation and backtesting return
`INSUFFICIENT_DATA`.

## Geography CSV

A coordinate file may be placed at `data/raw/geography.csv` with `place,latitude,longitude` columns. The pipeline uses Haversine distance and reports `distance_source=PUBLIC_DATA`; otherwise it reports `DEMO_PROXY`.

The default repository contains no downloaded public dataset. The verified keyless contextual sources are listed in the dataset registry and can be fetched by their adapters.

No official keyless Indian transport activity or migration-movement feed is
claimed here. A transport CSV can use the same mobility schema, but its source,
license, and access date must be registered before it is treated as public data.
