# Gati Shram

**Predictive mobility intelligence** is a production oriented prototype for estimating seasonal and circular migrant movement in India. It combines a FastAPI analytics backend with a judge facing Next.js presentation layer. It does not claim real time government mobility tracking, and synthetic outputs remain clearly labeled.

## Architecture

```text
DATA SOURCES
	|
	v
STATE NODE (raw PII stays inside state)
	|
	v
SANITIZATION / AGGREGATION
	|
	v
PRIVACY ENGINE
	|
	v
CENTRAL SIGNAL FUSION
	|
	v
DEEP GRAVITY + CAUSAL ANALYTICS
	|
	v
MIGRATION HEATMAPS / O-D MATRICES / CORRIDOR FORECASTS
```

The `StateNode` is the isolation boundary. Adapters ingest into the state-local raw-record store, aggregation removes worker identifiers, and only `CentralSignal` values are handed to the central analytics boundary. The privacy engine is currently an explicitly named placeholder: it does not provide cryptographic or differential-privacy guarantees. A validated, reviewed implementation must replace it before production use.

## Data sources

The replaceable adapter contract currently has demo implementations for:

- ONORC
- Indian Railways UTS
- e-Shram
- MGNREGA
- EPFO/ESIC
- BOCW
- State Worker Registry
- FASTag
- Employer/Contractor feeds
- Worker voluntary opt-in via missed call / WhatsApp

Every demo adapter returns marked mock data. Each can later be replaced with an API, CSV, database, or government data source without changing the State Node contract. Employer/contractor systems are a proposed zero-click ingestion source and require future integration, consent, security, and data-quality validation. The voluntary opt-in source also requires a future consent and channel implementation.

## Project layout

```text
app/
  main.py                 FastAPI application entry point
  api/v1/                 Versioned HTTP routes
  models/                 Raw, sanitized, and central data contracts
  schemas/                API schema package boundary
  services/               State Node orchestration
  adapters/               Replaceable data-source interfaces and demos
  analytics/              Central signal fusion boundary
  privacy/                Privacy transformation interface and placeholder
  config/                 Environment-backed settings
tests/                    Health and adapter/privacy-boundary tests
frontend/                 Next.js judge-facing presentation layer
```

## Run locally

Python 3.12+ is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Liveness endpoints are `GET /health` and `GET /api/v1/health`; interactive API documentation is at `/docs`. The fallback backend root at `/` is always available, while the full dashboard runs at `http://localhost:3000`.

In a second terminal, start the frontend:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`. `NEXT_PUBLIC_API_BASE_URL` points the frontend to the separately deployed FastAPI service; it is not assumed that Vercel hosts the Python backend.

Run the tests with:

```bash
pytest
```

The same service can be started with Docker Compose after copying `.env.example` to `.env`:

```bash
docker compose up --build
```

## Configuration

`.env.example` documents environment, database, API, privacy, and future external API credential settings. Secrets are never hardcoded and `.env` is ignored by git. The current demo does not require a database or external credentials.

## Implemented versus mocked

Implemented:

- FastAPI application with `/health` and `/api/v1/health`
- Typed adapter protocol and ten replaceable adapter classes
- State-local raw records, aggregate sanitization, and central signal contracts
- State Node ingestion and approved-signal flow
- Explicit privacy-engine interface and non-guaranteeing placeholder
- Environment configuration, Docker setup, and pytest coverage for the foundation

Mocked or deferred:

- All external data connectors and credentials
- Validated differential privacy or anonymization
- Persistent state-local and central databases
- Deep gravity, causal, forecasting, and corridor analytics
- Migration heatmaps, O-D matrices, and the frontend dashboard

The frontend presentation layer is implemented in `frontend/`; advanced ML and
production forecasting remain out of scope.

## Frontend and deployment

The frontend uses Next.js App Router, TypeScript, Geist Sans/Mono typography,
responsive CSS, and a centralized API client in `frontend/src/lib/api.ts`.
Pages include `/dashboard`, `/data`, `/model`, and `/architecture`; `/` opens
the dashboard. The UI consumes existing backend endpoints and shows `DEMO DATA`,
`REAL PUBLIC DATA`, `INSUFFICIENT_DATA`, `PROTOTYPE MODEL`, and fallback states
without inventing metrics.

For Vercel, import the `frontend/` directory as the project root and set:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-fastapi-service.example.com
```

Deploy the FastAPI service separately using the existing Docker or Uvicorn
setup, then set its `FRONTEND_ORIGIN` to the Vercel deployment URL. No
`vercel.json` is required for the standard Next.js build.

Vercel deployment for the frontend project:

```bash
npx vercel --cwd frontend
npx vercel --cwd frontend --prod
```

The Vercel CLI requires an authenticated Vercel account. Set
`NEXT_PUBLIC_API_URL` to the public FastAPI URL during project configuration;
set `frontend/` as the Vercel project Root Directory if configuring through the
dashboard, and keep the repository root available for the FastAPI service. The
frontend cannot deploy the Python API automatically.

## STEP 2 — Data Ingestion Pipeline

The working synthetic pipeline is:

```text
DATA SOURCES
	|
	v
ADAPTERS
	|
	v
STATE NODE
	|
	v
SANITIZATION
	|
	v
AGGREGATION
	|
	v
PRIVACY TRANSFORMATION
	|
	v
CENTRAL SIGNALS
```

The State Node executes `ingest() -> validate() -> sanitize() -> aggregate() -> privacy_transform() -> emit_central_signal()`. Raw records stay in the in-memory state-local layer. Worker IDs, phone numbers, Aadhaar-like identifiers, names, emails, and other direct identifiers are not represented by `SanitizedRecord` or `CentralMobilitySignal`.

### Step 2 status

Real:

- FastAPI routing, typed contracts, validation, aggregation, privacy boundary, central signal fusion, and automated tests.
- Environment-driven controls for minimum group size and the demo noise mechanism.

Synthetic or mocked:

- All ten source adapters and their records.
- State-local storage, central storage, external credentials, and external API calls.
- The privacy transformation. Its exact label is: **Prototype privacy transformation — requires formal DP calibration and security review before production.** It provides demo suppression and optional bounded noise only; it is not formal differential privacy.

Future government and employer integrations connect by replacing an adapter's `fetch_records()` implementation. Employer/contractor feeds remain a proposed zero-click ingestion source and require integration, consent, security, and data-quality validation before use.

### Step 2 API examples

Start the server with `uvicorn app.main:app --reload`, then run:

```bash
curl http://127.0.0.1:8000/api/v1/sources
curl http://127.0.0.1:8000/api/v1/signals/demo
curl -X POST http://127.0.0.1:8000/api/v1/state-node/ingest \
  -H 'Content-Type: application/json' \
  -d '{"state_code":"BR","source":"ONORC"}'
```

## STEP 3 — Predictive Intelligence Layer

Step 3 converts only the privacy-preserving central signals from Step 2 into
transparent, deterministic prototype estimates:

```text
CENTRAL SIGNALS
	|
	v
FEATURE ENGINEERING
	|
	v
DEEP GRAVITY PROTOTYPE
	|
	v
O-D MATRIX
	|
	v
CAUSAL FACTOR ANALYSIS
	|
	v
EARLY WARNING
	|
	v
CORRIDOR FORECAST
```

### Deep Gravity Prototype

The model extends a gravity-style flow equation with observed signal strength:

$$
\hat{F}_{ij}(t) = G \,\frac{OriginActivity_i(t)^\alpha \, DestinationActivity_j(t)^\gamma \, SignalStrength_{ij}(t)^\delta}{(Distance_{ij} + \epsilon)^\beta}
$$

`GravityParameters` are prototype values loaded from environment variables.
The implementation is deterministic and parameterized, but it is not a trained
deep-learning model and no accuracy claim is made. Distances use a clearly
labeled demo lookup table because no geographic dataset is connected.

### Step 3 status

Implemented:

- Deterministic feature engineering with demo distance proxies and temporal indicators.
- Deep Gravity Prototype with configurable alpha, gamma, beta, delta, epsilon, and quality flags.
- Raw and normalized origin-destination matrices.
- Transparent factor scoring labeled `DEMO`.
- Prototype Early-Warning Score with configurable thresholds.
- Moving-average corridor baseline forecast with configurable horizon.
- Analytics orchestration and five versioned API endpoints.

Not yet implemented:

- A trained ML model or neural network.
- Validated causal inference or causal significance.
- A real geographic distance dataset.
- Real migration ground truth or model evaluation.
- Production forecasting and operational early-warning claims.
- Real government or private APIs.

All Step 3 outputs are **DEMO / PROTOTYPE estimates**. Factor contributions
are heuristic scores, not statements that a factor causes migration. Forecasts
and risk scores must not be interpreted as actual Indian migrant movement
forecasts until real ground-truth data and formal evaluation are available.

### Step 3 API endpoints

- `GET /api/v1/analytics/demo` runs the complete intelligence pipeline.
- `GET /api/v1/analytics/od-matrix` returns raw and normalized O-D matrices.
- `GET /api/v1/analytics/early-warning` returns prototype risk scores.
- `GET /api/v1/analytics/corridors` returns baseline corridor forecasts.
- `GET /api/v1/analytics/factors` returns demo factor contributions.

## Real-World Data Readiness

Step 4 adds a public-data boundary without claiming live government access.
The API reports `DEMO DATA`, `REAL PUBLIC DATA`, or `MIXED DATA`, plus
`fallback_used`. The default mode is `DATA_MODE=demo`.

### Public datasets connected

The repository has verified, keyless adapters for these official contextual
sources. They are not fetched during normal demo requests:

| Dataset | Official source | Access type | Access date | Status |
| --- | --- | --- | --- | --- |
| World Bank India population | [World Bank API](https://api.worldbank.org/v2/country/IND/indicator/SP.POP.TOTL?format=json) | JSON API | 2026-09-17 | PUBLIC |
| World Bank India employment | [World Bank API](https://api.worldbank.org/v2/country/IND/indicator/SL.EMP.TOTL.SP.ZS?format=json) | JSON API | 2026-09-17 | PUBLIC |
| NASA POWER precipitation | [NASA POWER API](https://power.larc.nasa.gov/api/temporal/daily/point) | JSON API | 2026-09-17 | PUBLIC |

World Bank terms and NASA POWER data-access terms must be checked before
redistribution. No government migration API, authenticated private API, or
real-time movement tracker is connected.

### Implemented now

- Public dataset registry with source URL, access type, license note, geography, time granularity, status, and access date.
- Keyless World Bank and NASA POWER adapters.
- Reproducible local CSV ingestion for public mobility observations.
- Optional public-coordinate Haversine distances with `distance_source=PUBLIC_DATA`.
- Historical MAE, RMSE, valid MAPE, and R2 calculation.
- Temporal calibration and rolling backtesting.
- Data-quality reporting for row count, date/geography coverage, missing values, duplicates, source, and freshness.
- Explicit demo/public/hybrid modes and graceful synthetic fallback.

### Reproduce a public-data run

```bash
cp .env.example .env
# Place a licensed, documented file at data/raw/mobility.csv
# Optionally place place,latitude,longitude at data/raw/geography.csv
# Place separate observed historical flows at data/raw/historical_observations.csv
python -m app.data.ingest --input data/raw/mobility.csv --output data/processed/mobility.json
DATA_MODE=public uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/data/status
curl http://127.0.0.1:8000/api/v1/analytics/validation
curl http://127.0.0.1:8000/api/v1/analytics/backtest
```

### Still required for production

- Official government integrations and authenticated APIs where applicable.
- Larger documented historical ground truth and independent model evaluation.
- Security/privacy audit and formal privacy calibration.
- Operational monitoring, data contracts, and failure handling.
- Validated causal inference before using causal-effect language.
- A verified district/state characteristics and transport dataset.

All public-data metrics are computed only when observed rows are supplied.
Without them, validation and backtesting return `INSUFFICIENT_DATA`; no fake
accuracy, coverage, or causal significance is generated.
