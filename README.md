# GATI-SHRAMd

Privacy-first predictive mobility intelligence engine for estimating seasonal migrant movement using governed passive signals, state-level data nodes, and causal-spatial analytics.

## Initial architecture

The initial architecture is organized into five layers to keep data governance, model quality, and operational scale separated and testable:

1. **Data source layer**  
   Governed passive signals, public administrative datasets, and program-side mobility observations.
2. **Ingestion and standardization layer**  
   Batch/stream connectors normalize source schemas into a common mobility event contract.
3. **Privacy and governance layer**  
   De-identification, aggregation thresholds, role-based access control, and auditable policy checks before storage or model use.
4. **Intelligence and modeling layer**  
   Spatio-temporal feature engineering, causal context features, forecasting models, and uncertainty calibration.
5. **Decision and dissemination layer**  
   District/state forecasts, hotspot risk scoring, APIs, and dashboards for planning interventions.

## Predictive mobility intelligence framework

The framework is designed as an iterative loop:

1. **Collect**: ingest governed mobility and context signals.
2. **Transform**: generate geography-time aligned features (seasonality, origin-destination pressure, shock indicators).
3. **Predict**: run baseline + advanced forecasting models with confidence intervals.
4. **Explain**: attach driver attribution signals for policy interpretation.
5. **Act**: publish forecast outputs for planning and response workflows.
6. **Learn**: evaluate forecast drift and feed corrections into the next training cycle.

## Core data contracts

- **Mobility event**: `origin`, `destination`, `time_window`, `volume_band`, `signal_source`.
- **Context event**: `geography`, `time_window`, `factor_type`, `factor_intensity`.
- **Forecast output**: `geography`, `horizon`, `expected_flow_band`, `confidence`, `top_drivers`.

## Initial quality and safety controls

- Privacy-preserving thresholds before any disaggregated publication.
- Source and transformation lineage captured for each forecast batch.
- Bias checks across geography and worker-segment proxies.
- Model and data drift monitoring with retraining triggers.

## Phase-1 delivery scope

- Define canonical schemas for mobility/context/forecast entities.
- Build ingestion + feature pipeline for pilot geographies.
- Stand up baseline seasonal flow prediction with uncertainty bands.
- Expose outputs through a documented API-ready interface.
