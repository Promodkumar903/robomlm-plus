export type TerminalStatus =
  | "UNKNOWN"
  | "READY"
  | "PARTIAL"
  | "STALE"
  | "INVALID"
  | "ERROR";

export type TerminalMode =
  | "PAPER"
  | "DEMO"
  | "LIVE"
  | "UNKNOWN";

export type TerminalPriority =
  | "NORMAL"
  | "HIGH"
  | "CRITICAL";

export type TerminalContractStatus =
  | "CREATED"
  | "VALID"
  | "INVALID"
  | "READY";

export type TerminalDataState =
  | "COMPLETE"
  | "PARTIAL"
  | "MISSING"
  | "INVALID";

export type TerminalConsistency =
  | "CONSISTENT"
  | "CONDITIONAL"
  | "INCONSISTENT"
  | "UNKNOWN";

export type TerminalReadiness =
  | "READY"
  | "CONDITIONALLY_READY"
  | "NOT_READY"
  | "BLOCKED";

export type TerminalDecision =
  | "ALLOW"
  | "ALLOW_WITH_RESTRICTION"
  | "REVIEW_REQUIRED"
  | "BLOCK";

export type TerminalResolutionStatus =
  | "RESOLVED"
  | "CONDITIONAL"
  | "REVIEW_REQUIRED"
  | "BLOCKED";

export interface TerminalMarketContextRequest {
  market?: string;
  instrument?: string;
  symbol?: string;
  contract?: string;
  timeframe?: string;
  session?: string;
  market_phase?: string;
  mode?: TerminalMode;
  priority?: TerminalPriority;
  requested_fields?: string[];
  metadata?: Record<string, unknown>;
  request_id?: string;
  timestamp?: string;
}

export interface TerminalAssessment {
  market?: string;
  instrument?: string;
  symbol?: string;
  contract?: string;
  timeframe?: string;
  session?: string;
  market_phase?: string;
  status?: TerminalStatus;
  mode?: TerminalMode;
  source?: string;

  completeness?: number;
  context_quality?: number;
  confidence?: number;

  flags?: string[];
  warnings?: string[];
  unmet_requirements?: string[];

  notes?: string;
}

export interface TerminalPresentation {
  market?: string;
  instrument?: string;
  symbol?: string;
  contract?: string;
  timeframe?: string;
  session?: string;
  market_phase?: string;
  mode?: TerminalMode;
  source?: string;
  status?: TerminalStatus;

  completeness?: number;
  context_quality?: number;
  confidence?: number;

  flags?: string[];
  restrictions?: string[];
  warnings?: string[];
  errors?: string[];

  reason?: string;
  updated_at?: string;
  assessment_ready?: boolean;
}

export interface TerminalMarketContextResult {
  decision?: TerminalDecision;

  allowed?: boolean;
  restricted?: boolean;
  review_required?: boolean;
  blocked?: boolean;

  assessment?: TerminalAssessment;
  presentation?: TerminalPresentation;

  flags?: string[];
  restrictions?: string[];
  errors?: string[];
  warnings?: string[];

  reason?: string;
  timestamp?: string;

  resolution_status?: TerminalResolutionStatus;
}

export interface TerminalMarketContextSummary {
  engine?: string;
  version?: string;

  decision?: TerminalDecision;
  resolution_status?: TerminalResolutionStatus;

  allowed?: boolean;
  restricted?: boolean;
  review_required?: boolean;
  blocked?: boolean;

  market?: string;
  instrument?: string;
  symbol?: string;
  contract?: string;
  timeframe?: string;
  session?: string;
  market_phase?: string;
  mode?: TerminalMode;

  source?: string;
  status?: TerminalStatus;

  completeness?: number;
  context_quality?: number;
  confidence?: number;

  flags?: string[];
  restrictions?: string[];
  warnings?: string[];
  errors?: string[];

  reason?: string;
  updated_at?: string;
  assessment_ready?: boolean;
}