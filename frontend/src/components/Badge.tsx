import { StatusBadge } from "./StatusBadge";

export function riskTone(level: string): "teal" | "amber" | "red" | "neutral" {
  if (level === "HIGH") return "red";
  if (level === "MEDIUM") return "amber";
  if (level === "LOW") return "teal";
  return "neutral";
}

export function RiskBadge({ level }: { level: string }) {
  return <StatusBadge tone={riskTone(level)}>{level}</StatusBadge>;
}
