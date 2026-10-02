// frontend/src/types/terminal.ts
// ROBOMLM+ Terminal Contract — CANONICAL
// Source of truth: backend GET /api/terminal/frontend
// Contract version: ROBOMLM-TERMINAL-UI-1.0
//
// ⚠️ COMPLETE FILE — replace entire file. Do NOT append.

// ===========================================================================
// ROOT RESPONSE
// ===========================================================================

export interface TerminalContextResponse {
  contract_version: string;
  symbol: string;
  timeframe: string;
  context: TerminalContext;
  ui: TerminalUISelectors;
  sections: TerminalSections;
  controls: TerminalControls;
  authority: TerminalAuthority;
}

// ===========================================================================
// CONTEXT
// ===========================================================================

export interface TerminalContext {
  symbol: string;
  timeframe: string;
  market: TerminalMarketContext;
  instrument: unknown | null;
}

export interface TerminalMarketContext {
  snapshot: MarketSnapshot;
  health: MarketDataHealth;
}

// ===========================================================================
// MARKET SNAPSHOT
// ===========================================================================

export interface MarketIdentity {
  market: string;
  segment: string;
  country: string;
}

export interface InstrumentIdentity {
  symbol: string;
  instrument_type: string;
  instrument_id: string;
  asset_class: string | null;
}

export interface VenueIdentity {
  venue: string;
  venue_id: string;
}

export interface MarketObservation {
  observed_at: string;
  window_start: string | null;
  session_end_date: string | null;
  price: string | null;
  open: string | null;
  high: string | null;
  low: string | null;
  close: string | null;
  volume: string | null;
  turnover: string | null;
  transactions: number | null;
  bid: string | null;
  ask: string | null;
  open_interest: string | null;
  observation_kind: string;
  fields_present: string[];
}

export interface MarketTiming {
  source_timestamp: string;
  received_timestamp: string;
  observed_at: string;
  checked_at: string;
  latency_ms: string | null;
  freshness_seconds: number | null;
}

export interface MarketDataQuality {
  source: string;
  source_timestamp: string;
  received_timestamp: string;
  sequence: unknown | null;
  latency_ms: string | null;
  is_complete: boolean;
  is_stale: boolean;
  status: string;
  usable: boolean;
  freshness_seconds: number | null;
  missing_fields: string[];
  invalid_fields: string[];
  quality_flags: string[];
  reasons: string[];
  provider_quality_flags: string[];
}

export interface MarketState {
  session: string;
  halted: boolean;
  tradable: boolean;
  state_reason: string | null;
}

export interface MarketSnapshot {
  schema_version: string;
  snapshot_id: string | null;
  market: MarketIdentity;
  instrument: InstrumentIdentity;
  venue: VenueIdentity;
  contract: unknown | null;
  observed_at: string;
  observation: MarketObservation;
  timing: MarketTiming;
  data_quality: MarketDataQuality;
  provenance: Record<string, unknown>;
  state: MarketState;
  metadata: Record<string, unknown>;
}

export interface MarketDataHealth {
  status: string;
  usable: boolean;
  freshness_seconds: number;
  max_age_seconds: number;
  timestamp_valid: boolean;
  completeness_valid: boolean;
  source_valid: boolean;
  provider_quality_flags: string[];
  health_flags: string[];
  reasons: string[];
  checked_at: string;
  observed_at: string;
  source_timestamp: string;
  received_timestamp: string;
  metadata: Record<string, unknown>;
}

// ===========================================================================
// SECTIONS
// ===========================================================================

export interface TerminalSections {
  portfolio: TerminalSection<Record<string, never>>;
  market: TerminalSection<{
    snapshot: MarketSnapshot;
    health: MarketDataHealth;
  }>;
  chart: TerminalSection<Record<string, never>>;
  metrics: TerminalSection<Record<string, never>>;
  evidence: TerminalSection<EvidenceStageResult>;
  intelligence: TerminalSection<IntelligenceStageResult>;
  decision: TerminalSection<DecisionStageResult>;
  risk: TerminalSection<RiskStageResult>;
  cas: TerminalSection<CasStageResult>;
  log: TerminalSection<Record<string, never>>;
}

export interface TerminalSection<TData> {
  section: string;
  selectors: Record<string, string>;
  data: TData;
}

// ===========================================================================
// EVIDENCE
// ===========================================================================

export interface EvidenceItem {
  evidence_id: string;
  evidence_type: string;
  source: string;
  value: unknown;
  observed_at: string;
  market: string;
  instrument_id: string;
  timeframe: string;
  confidence: number | null;
  quality: string;
  description: string;
  metadata: Record<string, unknown>;
}

export interface EvidenceStageResult {
  available: boolean;
  executed: boolean;
  domain: string;
  module: string;
  function: string;
  arguments: string[];
  result: {
    status: string;
    package: {
      package_id: string;
      items: EvidenceItem[];
      market: string;
      instrument_id: string;
      timeframe: string;
      created_at: string;
      metadata: Record<string, unknown>;
    };
    normalized: {
      status: string;
      items: EvidenceItem[];
      normalized_count: number;
      rejected_count: number;
      errors: string[];
      warnings: string[];
      normalizer: string;
      version: string;
    };
    package_result: {
      status: string;
      accepted_count: number;
      rejected_count: number;
      duplicate_count: number;
      conflict_count: number;
      errors: string[];
      warnings: string[];
    };
    conflict_result: {
      status: string;
      package_id: string;
      conflicts: unknown[];
      analyzed_count: number;
      comparable_count: number;
      conflict_count: number;
      reason: string;
    };
    confidence_results: Record<
      string,
      {
        status: string;
        observation_count: number;
        evidence_count: number;
        warnings: string[];
      }
    >;
    reliability_results: Record<
      string,
      {
        status: string;
        source: string;
        state: string;
        warnings: string[];
      }
    >;
    input_count: number;
    accepted_count: number;
    rejected_count: number;
    errors: string[];
    warnings: string[];
    started_at: string;
    completed_at: string;
    orchestrator: string;
    version: string;
    reason: string;
  } | null;
  error: string | null;
}

// ===========================================================================
// INTELLIGENCE
// ===========================================================================

export interface IntelligenceStageResult {
  available: boolean;
  executed: boolean;
  domain: string;
  module: string;
  function: string;
  arguments: string[];
  result: {
    symbol: string;
    timeframe: string;
    intelligence_score: number;
    evidence_score: number;
    context_score: number;
    specialized_score: number;
    confidence_score: number;
    commitment_score: number;
    directional_bias: string;
    state: string;
    decision_ready: boolean;
    contradiction: boolean;
    contradiction_flags: string[];
    reasons: string[];
    evidence: {
      engine: string;
      formula: string;
      weights: Record<string, number>;
      layers: Record<string, number>;
      directional_bias: string;
      contradiction: boolean;
      contradiction_flags: string[];
      decision_ready: boolean;
      thresholds: Record<string, number>;
    };
    timestamp: string;
  } | null;
  error: string | null;
}

// ===========================================================================
// DECISION
// ===========================================================================

export interface DecisionStageResult {
  available: boolean;
  executed: boolean;
  domain: string;
  module: string;
  function: string;
  arguments: string[];
  result: {
    symbol: string;
    timeframe: string;
    decision: string;
    direction: string;
    decision_score: number;
    evidence_score: number;
    confidence_score: number;
    commitment_score: number;
    context_score: number;
    risk_score: number;
    timing_score: number;
    approved: boolean;
    confidence: number;
    gate_reasons: string[];
    conflict_flags: string[];
    evidence: {
      engine: string;
      formula: string;
      weights: Record<string, number>;
      direction: string;
      decision_score: number;
      approved: boolean;
      minimum_gates: Record<string, number>;
      context_score: number;
      risk_score: number;
      timing_score: number;
      directional_conflict: boolean;
      conflicts: string[];
    };
    timestamp: string;
  } | null;
  error: string | null;
}

// ===========================================================================
// RISK
// ===========================================================================

export interface RiskStageResult {
  available: boolean;
  executed: boolean;
  domain: string;
  module: string;
  function: string;
  arguments: string[];
  result: {
    request: Record<string, unknown>;
    requirements: {
      request_valid: boolean;
      readiness: string;
      completeness_score: number;
      warnings: string[];
    };
    assessment: {
      readiness: string;
      data_state: string;
      consistency: string;
      risk_score: number;
      confidence_score: number;
      completeness_score: number;
      risk_flags: string[];
      restrictions: string[];
      strengths: string[];
      weaknesses: string[];
      rationale: string;
    };
    action: {
      action_state: string;
      decision: string;
      pathway: string | null;
      direction: string | null;
      restrictions: string[];
      risk_flags: string[];
      reasons: string[];
      executable: boolean;
      requires_review: boolean;
      blocked: boolean;
    };
    result: {
      status: string;
      decision: string;
      risk_status: string;
      action_state: string;
      risk_score: number;
      risk_confidence: number;
      completeness_score: number;
      restrictions: string[];
      risk_flags: string[];
      reasons: string[];
      warnings: string[];
      pathway: string | null;
      direction: string | null;
      can_advance: boolean;
      requires_review: boolean;
      blocked: boolean;
      timestamp: string;
    };
    contract_state: string;
    contract_valid: boolean;
    timestamp: string;
  } | null;
  error: string | null;
}

// ===========================================================================
// CAS
// ===========================================================================

export interface CasGateExecution {
  gate: string;
  status: string;
  decision: string;
  allowed: boolean;
  restricted: boolean;
  review_required: boolean;
  blocked: boolean;
  score: number | null;
  confidence: number | null;
  flags: string[];
  restrictions: string[];
  reason: string;
  raw_result: unknown;
}

export interface CasStageResult {
  available: boolean;
  executed: boolean;
  domain: string;
  module: string;
  function: string;
  arguments: string[];
  result: {
    status: string;
    request: Record<string, unknown>;
    gate_executions: CasGateExecution[];
    result: {
      status: string;
      decision: string;
      allowed: boolean;
      restricted: boolean;
      review_required: boolean;
      blocked: boolean;
      pathway: string;
      score: number | null;
      confidence: number | null;
      gates_executed: string[];
      flags: string[];
      restrictions: string[];
      blocking_gates: string[];
      review_gates: string[];
      reason: string;
      request_id: string | null;
    };
    created_at: string;
    evaluated_at: string;
  } | null;
  error: string | null;
}

// ===========================================================================
// UI SELECTORS (legacy — kept for compatibility)
// ===========================================================================

export interface TerminalUISelectors {
  version: string;
  portfolio: Record<string, string>;
  market: Record<string, string>;
  chart: Record<string, string>;
  metrics: Record<string, string>;
  evidence: Record<string, string>;
  decision: Record<string, string>;
  manual_inputs: Record<string, string>;
  trade_controls: Record<string, string>;
  cas: Record<string, string>;
  log: Record<string, string>;
  discovery_context: Record<string, string>;
}

// ===========================================================================
// CONTROLS
// ===========================================================================

export interface TerminalControls {
  manual_inputs: Record<string, string>;
  trade_controls: Record<string, string>;
}

// ===========================================================================
// AUTHORITY
// ===========================================================================

export interface TerminalAuthority {
  frontend_is_authority: boolean;
  frontend_can_decide: boolean;
  frontend_can_authorize: boolean;
  frontend_can_execute: boolean;
  decision_authority: string;
  risk_authority: string;
  execution_authority: string;
}

// ===========================================================================
// CHART (frontend-only candle type — used for Binance fallback)
// ===========================================================================

export interface ChartCandle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ===========================================================================
// UI-ONLY TYPES (frontend state — not from backend)
// ===========================================================================

export type MarketId =
  | "CRYPTO"
  | "EQUITY"
  | "INDEX"
  | "FOREX"
  | "FUTURES"
  | "OPTIONS"
  | "COMMODITY";

export type ProviderId = "BINANCE" | "MASSIVE";

export interface TerminalSelection {
  market: MarketId;
  segment: string;
  instrument: string;
  provider: ProviderId;
  symbol: string;
  timeframe: string;
}

export type ProviderAvailability = "LIVE" | "UNAVAILABLE" | "NOT_SUPPORTED";

export interface QuickSymbol {
  label: string;
  symbol: string;
  market: MarketId;
  provider: ProviderId;
  availability: ProviderAvailability;
}

export interface WatchlistItem {
  symbol: string;
  market: MarketId;
  provider: ProviderId;
  last?: number;
  change?: number;
}

// ===========================================================================
// BACKWARD-COMPAT ALIASES (do not remove — existing imports may rely)
// ===========================================================================

export type TerminalFrontendResponse = TerminalContextResponse;

export type ActionState =
  | "CREATED"
  | "VALID"
  | "INVALID"
  | "BLOCKED"
  | "REVIEW"
  | "AUTHORIZED"
  | "PREPARED"
  | "SUBMITTED"
  | "REJECTED";