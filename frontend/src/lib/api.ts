export type DataStatus = {
  data_mode: "demo" | "public" | "hybrid" | string;
  data_classification: "DEMO DATA" | "REAL PUBLIC DATA" | "MIXED DATA" | string;
  fallback_used: boolean;
  datasets?: DatasetMetadata[];
};

export type DatasetMetadata = {
  dataset_id: string;
  name: string;
  source: string;
  url: string;
  access_type: string;
  license: string;
  geography: string;
  time_granularity: string;
  status: "PUBLIC" | "MOCK" | string;
  access_date: string;
  available?: boolean;
  fetched?: boolean;
};

export type CentralSignal = {
  origin: string;
  destination: string;
  time_window: string;
  signal_count: number;
  source_count: number;
  district: string | null;
  sources: string[];
};

export type GravityPrediction = {
  origin: string;
  destination: string;
  time_window: string;
  predicted_flow: number;
  quality_flag: string;
  district: string | null;
};

export type EarlyWarning = {
  origin: string;
  destination: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | string;
  drivers: string[];
  label: string;
  data_mode: string;
  evaluation_status: string;
};

export type FactorContribution = {
  factor: string;
  direction: string;
  relative_contribution: number;
  status: string;
};

export type CorridorForecast = {
  corridor: string;
  forecast_horizon: string;
  predicted_flow: number[];
  method: string;
};

export type DemoAnalytics = {
  central_signals: CentralSignal[];
  features: Array<Record<string, unknown>>;
  gravity_predictions: GravityPrediction[];
  od_matrix: Record<string, Record<string, number>>;
  normalized_od_matrix: Record<string, Record<string, number>>;
  factors: FactorContribution[];
  early_warnings: EarlyWarning[];
  corridor_forecasts: CorridorForecast[];
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
  dataset_ids: string[];
  distance_source: string;
  evaluation_status: string;
  data_quality: Record<string, unknown>;
};

export type EarlyWarningResponse = {
  status: string;
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
  scores: EarlyWarning[];
};

export type OdMatrixResponse = {
  status: string;
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
  od_matrix: Record<string, Record<string, number>>;
  normalized_od_matrix: Record<string, Record<string, number>>;
};

export type ValidationResponse = {
  evaluation_status: string;
  metrics: Record<string, number>;
  matched_observations: number;
  dataset_ids: string[];
  message: string;
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
};

export type BacktestResponse = {
  model: string;
  evaluation_status: string;
  metrics: Record<string, number>;
  splits: Array<Record<string, unknown>>;
  message: string;
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
};

export type ModelResponse = {
  model: string;
  status: string;
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
  baseline_parameters: Record<string, number>;
  calibration: Record<string, unknown>;
  training_period: string[];
  validation_period: string[];
  dataset_ids: string[];
};

export type QualityResponse = {
  data_mode: string;
  data_classification: string;
  fallback_used: boolean;
  dataset_ids: string[];
  distance_source: string;
  report: {
    row_count: number;
    date_coverage: { start: string | null; end: string | null };
    geographic_coverage: Record<string, number>;
    missing_values: Record<string, number>;
    duplicate_records: number;
    source: string;
    freshness_access_date: string;
    data_mode: string;
  };
};

function getApiBaseUrl(): string {
  const configured = (
    process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL
  )?.trim();
  if (configured) return configured.replace(/\/$/, "");

  if (typeof window !== "undefined") {
    const currentUrl = new URL(window.location.href);
    if (currentUrl.hostname.endsWith(".app.github.dev")) {
      currentUrl.hostname = currentUrl.hostname.replace(
        /-\d+\.app\.github\.dev$/,
        "-8000.app.github.dev",
      );
      currentUrl.pathname = "";
      currentUrl.search = "";
      currentUrl.hash = "";
      return currentUrl.origin;
    }
    if (currentUrl.hostname === "localhost" || currentUrl.hostname === "127.0.0.1") {
      return "http://127.0.0.1:8000";
    }
  }

  return "";
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; environment?: string }>("/api/v1/health"),
  dataStatus: () => request<DataStatus>("/api/v1/data/status"),
  dataSources: () => request<DataStatus>("/api/v1/data/sources"),
  demoAnalytics: () => request<DemoAnalytics>("/api/v1/analytics/demo"),
  earlyWarning: () => request<EarlyWarningResponse>("/api/v1/analytics/early-warning"),
  odMatrix: () => request<OdMatrixResponse>("/api/v1/analytics/od-matrix"),
  corridors: () => request<{ corridors: CorridorForecast[]; data_mode: string }>("/api/v1/analytics/corridors"),
  factors: () => request<{ factors: FactorContribution[]; data_mode: string }>("/api/v1/analytics/factors"),
  validation: () => request<ValidationResponse>("/api/v1/analytics/validation"),
  backtest: () => request<BacktestResponse>("/api/v1/analytics/backtest"),
  model: () => request<ModelResponse>("/api/v1/analytics/model"),
  quality: () => request<QualityResponse>("/api/v1/analytics/data-quality"),
};
