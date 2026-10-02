import { ReactNode } from "react";

export type StatusTone = "ok" | "warn" | "bad" | "muted" | "info";

export interface StatusBadgeProps {
  label?: string;
  tone?: StatusTone;
  status?: string;
  children?: ReactNode;
  className?: string;
}

function toneFromStatus(status?: string): StatusTone {
  if (!status) return "muted";
  const s = status.toUpperCase();
  if (["READY", "VALID", "LIVE", "OK", "AUTHORIZED", "APPROVED"].includes(s)) return "ok";
  if (["REVIEW", "WAITING", "PENDING", "INSUFFICIENT", "UNKNOWN"].includes(s)) return "warn";
  if (["ERROR", "INVALID", "BLOCKED", "REJECTED", "FAILED"].includes(s)) return "bad";
  return "info";
}

export default function StatusBadge({
  label,
  tone,
  status,
  children,
  className,
}: StatusBadgeProps) {
  const resolvedTone = tone ?? toneFromStatus(status);
  const text = children ?? label ?? status ?? "—";

  return (
    <span className={`rbm-status-badge rbm-status-${resolvedTone} ${className ?? ""}`.trim()}>
      {text}
    </span>
  );
}