type StatusBadgeProps = {
  children: React.ReactNode;
  tone?: "teal" | "amber" | "red" | "blue" | "neutral";
};

export function StatusBadge({ children, tone = "neutral" }: StatusBadgeProps) {
  return <span className={`status-badge ${tone}`}>{children}</span>;
}
