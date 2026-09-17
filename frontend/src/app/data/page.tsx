"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EmptyState, ErrorState, LoadingState } from "@/components/States";
import { SectionHeader } from "@/components/SectionHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { api, type DataStatus } from "@/lib/api";

export default function DataPage() {
  const [status, setStatus] = useState<DataStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api.dataSources().then(setStatus).catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load provenance.")); }, []);
  if (error) return <AppShell><ErrorState detail={error} /></AppShell>;
  if (!status) return <AppShell><LoadingState label="Loading dataset registry..." /></AppShell>;
  return <AppShell>
    <div className="page-heading"><div><div className="eyebrow">Data governance</div><h1>Data provenance</h1><p className="lede">Every source is identified by its access type, coverage, terms, and current availability. A public registry entry does not mean the data was fetched for this run.</p></div><StatusBadge tone={status.data_classification === "DEMO DATA" ? "amber" : "teal"}>{status.data_classification}</StatusBadge></div>
    <div className="card panel section"><SectionHeader eyebrow="Current run" title="Provenance state" /><div className="kv-list"><div className="kv"><span className="kv-label">Data mode</span><span className="kv-value">{status.data_mode.toUpperCase()}</span></div><div className="kv"><span className="kv-label">Fallback used</span><span className="kv-value">{status.fallback_used ? "YES" : "NO"}</span></div></div></div>
    <section className="section"><SectionHeader eyebrow="Dataset registry" title="Registered sources" detail="Official metadata from the API" /><div className="card panel-tight table-wrap">{!status.datasets?.length ? <EmptyState title="No registry entries" detail="The backend returned no dataset metadata." /> : <table><thead><tr><th>Dataset</th><th>Source</th><th>Type</th><th>Coverage</th><th>Access date</th><th>Status</th></tr></thead><tbody>{status.datasets.map((dataset) => <tr key={dataset.dataset_id}><td><strong>{dataset.name}</strong><div className="small muted mono">{dataset.dataset_id}</div></td><td>{dataset.source}</td><td className="mono small">{dataset.access_type}</td><td>{dataset.geography} / {dataset.time_granularity}</td><td className="mono small">{dataset.access_date}</td><td><StatusBadge tone={dataset.status === "PUBLIC" ? "teal" : "amber"}>{dataset.status === "PUBLIC" ? "VERIFIED PUBLIC SOURCE" : "OPERATOR-SUPPLIED"}</StatusBadge></td></tr>)}</tbody></table>}</div></section>
    <div className="callout section"><strong>Interpretation note</strong>Demo mobility records remain synthetic. No real time government mobility tracking or authenticated private source is implied by this registry.</div>
  </AppShell>;
}
