import type {
  StatusTone
} from "./types";

import {
  el,
  text
} from "./dom";

export function createStatusBadge(
  label: string,
  tone: StatusTone = "neutral"
): HTMLElement {
  const badge = el(
    "span",
    "ui-status-badge"
  );

  badge.dataset.tone = tone;

  badge.appendChild(
    text(label)
  );

  return badge;
}

export function statusTone(
  status: string | null | undefined
): StatusTone {
  switch (
    String(status ?? "")
      .toLowerCase()
  ) {
    case "ok":
    case "ready":
    case "healthy":
    case "success":
    case "passed":
      return "success";

    case "warning":
    case "degraded":
    case "pending":
      return "warning";

    case "error":
    case "failed":
    case "danger":
    case "blocked":
      return "danger";

    case "info":
    case "running":
      return "info";

    default:
      return "neutral";
  }
}