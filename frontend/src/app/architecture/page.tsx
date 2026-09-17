import { AppShell } from "@/components/AppShell";
import { SectionHeader } from "@/components/SectionHeader";
import { StatusBadge } from "@/components/StatusBadge";

const nodes = [
  ["01", "Data sources", "Adapters keep external access replaceable."],
  ["02", "State Node", "Raw worker records stay local."],
  ["03", "Validation", "Malformed and incomplete rows are visible."],
  ["04", "Sanitization", "Direct identifiers leave the local boundary."],
  ["05", "Aggregation", "Signals become route and time-window summaries."],
  ["06", "Privacy transformation", "Prototype suppression/noise only; not formal DP."],
  ["07", "Central signal fusion", "Only approved aggregate signals enter analytics."],
  ["08", "Gravity + O-D + factors", "Prototype intelligence layer."],
  ["09", "Warning + forecast", "Transparent risk and baseline outputs."],
];

export default function ArchitecturePage() {
  return <AppShell>
    <div className="page-heading"><div><div className="eyebrow">System design</div><h1>Architecture</h1><p className="lede">A state aware processing boundary separates raw worker level ingestion from central mobility intelligence.</p></div><StatusBadge tone="teal">PRIVACY BOUNDARY</StatusBadge></div>
    <section className="card panel section"><SectionHeader eyebrow="Processing path" title="From source to signal" /><div className="architecture">{nodes.map(([number, title, detail], index) => <div className={`arch-node ${index === 1 || index === 2 || index === 3 || index === 4 || index === 5 ? "boundary" : ""}`} key={number}><span>{number}</span><strong>{title}</strong><p className="small muted" style={{ margin: "10px 0 0" }}>{detail}</p></div>)}</div></section>
    <div className="page-grid section"><section className="card panel"><SectionHeader eyebrow="State boundary" title="What stays local" /><p className="small muted">Raw worker identifiers remain inside the state processing boundary. Adapters can be replaced without changing the central analytics contract.</p><ul className="list"><li>Worker IDs and contact details</li><li>Source native records before sanitization</li><li>Local validation and aggregation state</li></ul></section><section className="card panel"><SectionHeader eyebrow="Central boundary" title="What is emitted" /><p className="small muted">Central analytics operate on aggregated and sanitized mobility signals. They contain route dimensions, time windows, counts, and source coverage.</p><ul className="list"><li>Origin destination signals and normalized matrices</li><li>Prototype gravity estimates</li><li>Risk, factor, and forecast outputs</li></ul></section></div>
    <div className="callout section"><strong>Privacy implementation status</strong>The current privacy transformation is a prototype boundary and requires formal differential-privacy calibration and security review before production use.</div>
  </AppShell>;
}
