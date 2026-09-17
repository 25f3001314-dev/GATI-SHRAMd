type MetricCardProps = {
  label: string;
  value: string;
  detail?: string;
};

export function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <article className="card metric-card">
      <span className="metric-label">{label}</span>
      <strong className="metric-value mono">{value}</strong>
      {detail ? <span className="metric-detail">{detail}</span> : null}
    </article>
  );
}
