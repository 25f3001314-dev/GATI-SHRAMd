export function LoadingState({ label = "Loading API data..." }: { label?: string }) {
  return <div className="loading">{label}</div>;
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return <div className="empty-state"><strong>{title}</strong>{detail}</div>;
}

export function ErrorState({ detail = "The API could not be reached." }: { detail?: string }) {
  return <div className="error-state">{detail} Check that FastAPI is running and refresh this page.</div>;
}
