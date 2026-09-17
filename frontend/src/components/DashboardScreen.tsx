"use client";

import { useEffect, useState } from "react";
import { api, type BacktestResponse, type CorridorForecast, type DataStatus, type DemoAnalytics, type EarlyWarningResponse, type FactorContribution, type ModelResponse, type OdMatrixResponse, type ValidationResponse } from "@/lib/api";
import { AppShell } from "./AppShell";
import { MetricCard } from "./MetricCard";
import { SectionHeader } from "./SectionHeader";
import { EmptyState, ErrorState, LoadingState } from "./States";
import { RiskBadge } from "./Badge";
import { StatusBadge } from "./StatusBadge";

const numberFormat = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 });

function formatValue(value: number | undefined) {
  return value === undefined ? "Not available" : numberFormat.format(value);
}

function classificationTone(classification: string) {
  return classification === "REAL PUBLIC DATA" ? "teal" : classification === "MIXED DATA" ? "blue" : "amber";
}

export function DashboardScreen() {
  const [payload, setPayload] = useState<{
    status: DataStatus;
    demo: DemoAnalytics;
    warning: EarlyWarningResponse;
    od: OdMatrixResponse;
    model: ModelResponse;
    validation: ValidationResponse;
    backtest: BacktestResponse;
    corridors: CorridorForecast[];
    factors: FactorContribution[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.dataStatus(),
      api.demoAnalytics(),
      api.earlyWarning(),
      api.odMatrix(),
      api.model(),
      api.validation(),
      api.backtest(),
      api.corridors(),
      api.factors(),
    ])
      .then(([status, demo, warning, od, model, validation, backtest, corridors, factors]) => setPayload({ status, demo, warning, od, model, validation, backtest, corridors: corridors.corridors, factors: factors.factors }))
      .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load dashboard data."));
  }, []);

  if (error) {
    return <AppShell><ErrorState detail={error} /></AppShell>;
  }
  if (!payload) {
    return <AppShell><LoadingState label="Loading mobility intelligence workspace..." /></AppShell>;
  }

  const { status, demo, warning, od, model, validation, backtest, corridors, factors } = payload;
  const maxSources = Math.max(...demo.central_signals.map((signal) => signal.source_count), 0);
  const warningCount = warning.scores.filter((score) => score.risk_level !== "LOW").length;
  const maxFlow = Math.max(...Object.values(od.od_matrix).flatMap((destinations) => Object.values(destinations)), 0);
  const warningByRoute = new Map(warning.scores.map((score) => [`${score.origin}::${score.destination}`, score]));

  return (
    <AppShell>
      <div className="page-heading">
        <div>
          <div className="eyebrow">Overview / synthetic signal workspace</div>
          <h1>Mobility intelligence</h1>
          <p className="lede">A governed view of aggregated mobility signals, prototype forecasts, and the evidence available for evaluation.</p>
        </div>
        <StatusBadge tone={classificationTone(status.data_classification)}>{status.data_classification}</StatusBadge>
      </div>

      <section className="metrics-grid grid" aria-label="System status">
        <MetricCard label="Data mode" value={status.data_mode.toUpperCase()} detail="Configured runtime mode" />
        <MetricCard label="O-D pairs" value={formatValue(demo.central_signals.length)} detail="Aggregated route signals" />
        <MetricCard label="Source span" value={formatValue(maxSources)} detail="Maximum sources represented" />
        <MetricCard label="Warning corridors" value={formatValue(warningCount)} detail="Prototype scores above LOW" />
      </section>

      <section className="card panel section" aria-labelledby="status-heading">
        <SectionHeader eyebrow="System status" title="Current evidence boundary" detail="API-backed" />
        <div className="kv-list">
          <div className="kv"><span className="kv-label">Data classification</span><StatusBadge tone={classificationTone(status.data_classification)}>{status.data_classification}</StatusBadge></div>
          <div className="kv"><span className="kv-label">Fallback used</span><span className="kv-value">{status.fallback_used ? "YES" : "NO"}</span></div>
          <div className="kv"><span className="kv-label">Evaluation status</span><StatusBadge tone={demo.evaluation_status === "DEMO_ONLY" ? "amber" : "blue"}>{demo.evaluation_status}</StatusBadge></div>
          <div className="kv"><span className="kv-label">Distance source</span><span className="kv-value">{demo.distance_source}</span></div>
        </div>
      </section>

      <section className="section" aria-labelledby="corridors-heading">
        <SectionHeader eyebrow="Mobility overview" title="Top corridors" detail="Central aggregated signals" />
        <div className="card panel-tight table-wrap">
          {demo.central_signals.length === 0 ? <EmptyState title="No corridors available" detail="The API returned no central mobility signals." /> : (
            <table><thead><tr><th>Origin</th><th>Destination</th><th>Flow signal</th><th>Risk</th><th>Data status</th></tr></thead><tbody>
              {demo.central_signals.map((signal) => {
                const score = warningByRoute.get(`${signal.origin}::${signal.destination}`);
                return <tr key={`${signal.origin}-${signal.destination}-${signal.time_window}`}><td className="route">{signal.origin}</td><td><span className="route-arrow">→</span>{signal.destination}</td><td className="table-number">{formatValue(signal.signal_count)} <span className="muted">/ {signal.time_window}</span></td><td>{score ? <RiskBadge level={score.risk_level} /> : <span className="muted">Not available</span>}</td><td><StatusBadge tone="amber">{status.data_classification}</StatusBadge></td></tr>;
              })}
            </tbody></table>
          )}
        </div>
      </section>

      <section className="two-column grid section">
        <div className="card panel">
          <SectionHeader eyebrow="Origin-destination" title="Predicted flow matrix" detail="Gravity prototype" />
          {Object.keys(od.od_matrix).length === 0 ? <EmptyState title="No O-D flow available" detail="Predicted flows will appear when central signals are available." /> : Object.entries(od.od_matrix).map(([origin, destinations]) => Object.entries(destinations).map(([destination, flow]) => <div className="bar-row" key={`${origin}-${destination}`}><span className="route">{origin} <span className="route-arrow">→</span> {destination}</span><span className="bar-track"><span className="bar-fill" style={{ width: `${maxFlow ? Math.max((flow / maxFlow) * 100, 3) : 0}%` }} /></span><span className="table-number">{formatValue(flow)}</span></div>))}
          <p className="small muted" style={{ margin: "16px 0 0" }}>Normalized shares are available on the O-D matrix API endpoint.</p>
        </div>
        <div className="card panel">
          <SectionHeader eyebrow="Model and validation" title="Evidence status" />
          <div className="kv-list">
            <div className="kv"><span className="kv-label">Model</span><span className="kv-value">{model.model}</span></div>
            <div className="kv"><span className="kv-label">Calibration</span><StatusBadge tone="blue">{String(model.calibration.calibration_status || "NOT RUN")}</StatusBadge></div>
            <div className="kv"><span className="kv-label">Historical validation</span><StatusBadge tone={validation.evaluation_status === "VALIDATED" ? "teal" : "amber"}>{validation.evaluation_status}</StatusBadge></div>
            <div className="kv"><span className="kv-label">Backtest</span><StatusBadge tone={backtest.evaluation_status === "VALIDATED" ? "teal" : "amber"}>{backtest.evaluation_status}</StatusBadge></div>
          </div>
          <div className="callout" style={{ marginTop: 18 }}><strong>Prototype interpretation</strong>Observed mobility data has not been supplied for historical evaluation. No accuracy or causal claim is shown.</div>
        </div>
      </section>

      <section className="card panel section" aria-labelledby="warning-heading">
        <SectionHeader eyebrow="Early warning" title="Prototype Early-Warning Score" detail="Not a government alert" />
        {warning.scores.length === 0 ? <EmptyState title="No warning scores available" detail="The API returned no corridor risk scores." /> : <div className="table-wrap"><table><thead><tr><th>Corridor</th><th>Score</th><th>Level</th><th>Drivers</th><th>Evaluation</th></tr></thead><tbody>{warning.scores.map((score) => <tr key={`${score.origin}-${score.destination}`}><td className="route">{score.origin} <span className="route-arrow">→</span> {score.destination}</td><td className="table-number">{score.risk_score.toFixed(4)}</td><td><RiskBadge level={score.risk_level} /></td><td><div className="driver-list">{score.drivers.length ? score.drivers.map((driver) => <span className="driver" key={driver}>{driver}</span>) : <span className="muted">No elevated driver</span>}</div></td><td><StatusBadge tone="amber">{score.evaluation_status}</StatusBadge></td></tr>)}</tbody></table></div>}
      </section>

      <section className="two-column grid section">
        <div className="card panel">
          <SectionHeader eyebrow="Corridor outlook" title="Baseline forecasts" detail="Prototype, not a live forecast" />
          {corridors.length === 0 ? <EmptyState title="No corridor forecasts" detail="The API returned no forecast corridors." /> : <div className="table-wrap"><table><thead><tr><th>Corridor</th><th>Horizon</th><th>Projected flow</th></tr></thead><tbody>{corridors.map((corridor) => <tr key={corridor.corridor}><td className="route">{corridor.corridor}</td><td className="small muted">{corridor.forecast_horizon}</td><td className="table-number">{corridor.predicted_flow.length ? formatValue(corridor.predicted_flow[0]) : "Not available"}</td></tr>)}</tbody></table></div>}
        </div>
        <div className="card panel">
          <SectionHeader eyebrow="Factor analysis" title="Model feature contributions" detail="DEMO associations" />
          {factors.length === 0 ? <EmptyState title="No factor contributions" detail="The API returned no factor associations." /> : factors.slice().sort((a, b) => b.relative_contribution - a.relative_contribution).slice(0, 5).map((factor) => <div className="bar-row" key={factor.factor}><span className="small">{factor.factor.replaceAll("_", " ")}</span><span className="bar-track"><span className="bar-fill" style={{ width: `${Math.max(factor.relative_contribution * 100, factor.relative_contribution ? 3 : 0)}%` }} /></span><span className="table-number">{(factor.relative_contribution * 100).toFixed(1)}%</span></div>)}
          <p className="small muted" style={{ margin: "16px 0 0" }}>These are prototype feature contributions, not validated causal effects.</p>
        </div>
      </section>
    </AppShell>
  );
}
