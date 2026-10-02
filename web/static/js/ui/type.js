export type StatusTone =
  | "neutral"
  | "info"
  | "success"
  | "warning"
  | "danger";

export interface CardOptions {
  title: string;
  subtitle?: string;
  tone?: StatusTone;
  className?: string;
}

export interface TableColumn<T> {
  key: string;
  label: string;
  render?: (
    value: unknown,
    row: T
  ) => string | HTMLElement;
}

export interface TableOptions<T> {
  columns: TableColumn<T>[];
  emptyMessage?: string;
}

export interface EvidenceItem {
  id?: string;
  source?: string;
  title?: string;
  claim?: string;
  timestamp?: string;
  confidence?: number | null;
  status?: string;
  [key: string]: unknown;
}

export interface DecisionPanelData {
  decision?: string;
  action?: string;
  rationale?: string;
  confidence?: number | null;
  timestamp?: string;
  evidenceIds?: string[];
  [key: string]: unknown;
}

export interface RiskPanelData {
  level?: string;
  status?: string;
  summary?: string;
  exposure?: number | null;
  maxLoss?: number | null;
  warnings?: string[];
  gates?: unknown[];
  [key: string]: unknown;
}