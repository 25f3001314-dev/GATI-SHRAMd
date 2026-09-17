"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/States";
import { SectionHeader } from "@/components/SectionHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { api, type BacktestResponse, type ModelResponse, type ValidationResponse } from "@/lib/api";

export default function ModelPage() {
  const [data, setData] = useState<{ model: ModelResponse; validation: ValidationResponse; backtest: BacktestResponse } | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { Promise.all([api.model(), api.validation(), api.backtest()]).then(([model, validation, backtest]) => setData({ model, validation, backtest })).catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load model status.")); }, []);
  if (error) return <AppShell><ErrorState detail={error} /></AppShell>;
  if (!data) return <AppShell><LoadingState label="Loading model and validation status..." /></AppShell>;
  const { model, validation, backtest } = data;
  return <AppShell>
    <div className="page-heading"><div><div className="eyebrow">Technical model record</div><h1>Model status</h1><p className="lede">A transparent gravity-style prototype. Parameters and evaluation state are read from the backend; no trained model or performance claim is presented.</p></div><StatusBadge tone="amber">PROTOTYPE MODEL</StatusBadge></div>
    <section className="card panel"><SectionHeader eyebrow="Mathematical form" title="Deep Gravity Prototype" /><div className="formula">F̂ᵢⱼ(t) = G × OriginActivityᵢ(t)^α × DestinationActivityⱼ(t)^γ × SignalStrengthᵢⱼ(t)^δ / (Distanceᵢⱼ + ε)^β</div><p className="small muted" style={{ margin: "16px 0 0" }}>Distance uses PUBLIC_DATA coordinates when supplied, otherwise the documented Step 3 demo proxy.</p></section>
    <div className="page-grid section"><section className="card panel"><SectionHeader eyebrow="Parameters" title="Current baseline" /><div className="kv-list">{Object.entries(model.baseline_parameters).map(([key, value]) => <div className="kv" key={key}><span className="kv-label mono">{key}</span><span className="kv-value">{value}</span></div>)}</div></section><section className="card panel"><SectionHeader eyebrow="Evidence" title="Validation record" /><div className="kv-list"><div className="kv"><span className="kv-label">Calibration</span><StatusBadge tone="blue">{String(model.calibration.calibration_status || "NOT RUN")}</StatusBadge></div><div className="kv"><span className="kv-label">Historical validation</span><StatusBadge tone={validation.evaluation_status === "VALIDATED" ? "teal" : "amber"}>{validation.evaluation_status}</StatusBadge></div><div className="kv"><span className="kv-label">Temporal backtest</span><StatusBadge tone={backtest.evaluation_status === "VALIDATED" ? "teal" : "amber"}>{backtest.evaluation_status}</StatusBadge></div><div className="kv"><span className="kv-label">Dataset IDs</span><span className="kv-value">{model.dataset_ids.length ? model.dataset_ids.join(", ") : "None"}</span></div></div></section></div>
    <section className="card panel section"><SectionHeader eyebrow="Feature semantics" title="How the prototype reads signals" /><ul className="list"><li>Origin activity and destination activity summarize aggregate signal volume.</li><li>Signal strength represents the relative observed signal in the current input set.</li><li>Distance is a transparent proxy unless public coordinates are supplied.</li><li>Calibration requires separate historical observed flows and a temporal split.</li></ul></section>
    {validation.evaluation_status !== "VALIDATED" ? <div className="callout section"><strong>Historical validation unavailable</strong>Observed mobility data has not been supplied for evaluation. Metrics are intentionally omitted.</div> : null}
  </AppShell>;
}
