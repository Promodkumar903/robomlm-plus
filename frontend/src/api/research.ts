// C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts

/**
 * ROBOMLM_PLUS
 * Research / Intelligence API Adapter
 *
 * Responsibility:
 * - Fetch the authoritative backend Research/Terminal intelligence payload.
 * - Normalize common backend naming variants.
 * - Preserve backend states exactly.
 * - Never calculate proprietary intelligence formulas.
 * - Never invent BUY/SELL decisions.
 * - Never invent scores, grades, thresholds, or authority.
 */

export type Decision =
  | "BUY"
  | "SELL"
  | "HOLD"
  | "WAIT"
  | "REVIEW"
  | "BLOCKED"
  | "UNAVAILABLE";

export type AuthorityState =
  | "AVAILABLE"
  | "READY"
  | "REVIEW"
  | "BLOCKED"
  | "DISABLED"
  | "UNAVAILABLE"
  | "UNKNOWN";

export interface ResearchInstrument {
  symbol?: string;
  market?: string;
  segment?: string;
  venue?: string;
  country?: string;
  instrumentType?: string;
  price?: number | null;
  changePercent?: number | null;
  liveState?: string;
}

export interface ResearchDecision {
  decision: Decision;
  direction?: string;
  score?: number | null;
  grade?: string | null;
  state?: string;
  status?: string;
  ready?: boolean;
  reason?: string;
  message?: string;
}

export interface ResearchIntelligence {
  state?: string;
  score?: number | null;
  grade?: string | null;
  direction?: string;
  items?: ResearchEngine[];
  contradictions?: ResearchContradiction[];
}

export interface ResearchEngine {
  id: string;
  name: string;
  shortName?: string;
  score?: number | null;
  grade?: string | null;
  state?: string;
  direction?: string;
  status?: string;
  message?: string;
  reason?: string;
  source?: string;
  timestamp?: string;
}

export interface ResearchStage {
  id: string;
  label: string;
  state:
    | "PASS"
    | "ACTIVE"
    | "PENDING"
    | "REVIEW"
    | "BLOCKED"
    | "FAILED"
    | "UNAVAILABLE"
    | "UNKNOWN";
  message?: string;
}

export interface ResearchEvidence {
  id: string;
  source?: string;
  dimension?: string;
  value?: unknown;
  disposition?: string;
  validity?: string;
  reason?: string;
  observedAt?: string;
}

export interface ResearchEvidenceState {
  state?: string;
  status?: string;
  packageState?: string;
  supportingCount?: number;
  conflictingCount?: number;
  acceptedCount?: number;
  rejectedCount?: number;
  provenance?: string;
  temporal?: string;
  items?: ResearchEvidence[];
}

export interface ResearchContradiction {
  id: string;
  type?: string;
  severity?: string;
  state?: string;
  message?: string;
  resolution?: string;
  source?: string;
}

export interface ResearchDecisionMap {
  marketState?: string;
  transition?: string;
  scenario?: string;
  direction?: string;
  structure?: string;
  liquidity?: string;
  accumulation?: string;
  distribution?: string;
  volatility?: string;
  timing?: string;
  regime?: string;
}

export interface ResearchAction {
  state?: AuthorityState;
  enabled?: boolean;
  reason?: string;
  message?: string;
}

export interface ResearchTradeAuthority {
  userPolicy?: {
    enabled?: boolean;
    minimumScore?: number | null;
    belowMinimumAction?: Decision;
    description?: string;
  };

  auto?: {
    state?: AuthorityState;
    decision?: Decision;
    enabled?: boolean;
    reason?: string;
    message?: string;
  };

  manual?: {
    state?: AuthorityState;
    decision?: Decision;
    enabled?: boolean;
    reason?: string;
    message?: string;
  };

  actions?: {
    buy?: ResearchAction;
    sell?: ResearchAction;
    hold?: ResearchAction;
    wait?: ResearchAction;
  };
}

export interface ResearchScenarios {
  id?: string;
  type?: string;
  direction?: string;
  state?: string;
  description?: string;
  invalidation?: string;
}

export interface ResearchSystemState {
  marketData?: string;
  evidence?: string;
  intelligence?: string;
  risk?: string;
  execution?: string;
  cas?: string;
}

export interface ResearchApiState {
  requestId?: string;
  generatedAt?: string;

  instrument: ResearchInstrument;

  decision: ResearchDecision;

  intelligence: ResearchIntelligence;

  engines: ResearchEngine[];

  stages: ResearchStage[];

  decisionMap: ResearchDecisionMap;

  evidence: ResearchEvidenceState;

  contradictions: ResearchContradiction[];

  tradeAuthority: ResearchTradeAuthority;

  scenarios: ResearchScenarios[];

  system: ResearchSystemState;

  raw: unknown;
}

export interface ResearchApiError {
  code: string;
  message: string;
  retryable: boolean;
  requestId?: string;
}

export class ResearchApiException extends Error {
  readonly code: string;
  readonly retryable: boolean;
  readonly requestId?: string;

  constructor(error: ResearchApiError) {
    super(error.message);

    this.name = "ResearchApiException";
    this.code = error.code;
    this.retryable = error.retryable;
    this.requestId = error.requestId;
  }
}

const RESEARCH_ENDPOINT =
  "/api/terminal/frontend";

/**
 * Do not use Number(value) blindly for backend objects.
 */
function numberOrNull(value: unknown): number | null {
  if (
    typeof value === "number" &&
    Number.isFinite(value)
  ) {
    return value;
  }

  if (
    typeof value === "string" &&
    value.trim() !== ""
  ) {
    const parsed = Number(value);

    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return null;
}

function stringOrUndefined(
  value: unknown,
): string | undefined {
  if (
    value === undefined ||
    value === null
  ) {
    return undefined;
  }

  const text = String(value).trim();

  return text === "" ? undefined : text;
}

function booleanOrUndefined(
  value: unknown,
): boolean | undefined {
  return typeof value === "boolean"
    ? value
    : undefined;
}

function isRecord(
  value: unknown,
): value is Record<string, unknown> {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}

function first(
  ...values: unknown[]
): unknown {
  for (const value of values) {
    if (
      value !== undefined &&
      value !== null
    ) {
      return value;
    }
  }

  return undefined;
}

function record(
  value: unknown,
): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function array(
  value: unknown,
): unknown[] {
  return Array.isArray(value) ? value : [];
}

function normalizeDecision(
  value: unknown,
): Decision {
  const normalized =
    String(value ?? "")
      .trim()
      .toUpperCase();

  switch (normalized) {
    case "BUY":
    case "SELL":
    case "HOLD":
    case "WAIT":
    case "REVIEW":
    case "BLOCKED":
      return normalized;

    default:
      return "UNAVAILABLE";
  }
}

function normalizeAuthority(
  value: unknown,
): AuthorityState {
  const normalized =
    String(value ?? "")
      .trim()
      .toUpperCase();

  switch (normalized) {
    case "AVAILABLE":
    case "READY":
    case "REVIEW":
    case "BLOCKED":
    case "DISABLED":
    case "UNAVAILABLE":
      return normalized;

    default:
      return "UNKNOWN";
  }
}

function normalizeStage(
  value: unknown,
): ResearchStage["state"] {
  const normalized =
    String(value ?? "")
      .trim()
      .toUpperCase();

  switch (normalized) {
    case "PASS":
    case "ACTIVE":
    case "PENDING":
    case "REVIEW":
    case "BLOCKED":
    case "FAILED":
    case "UNAVAILABLE":
      return normalized;

    default:
      return "UNKNOWN";
  }
}

/**
 * Backend responses may be wrapped by:
 *
 * {
 *   data: {...}
 * }
 *
 * or
 *
 * {
 *   result: {...}
 * }
 *
 * or
 *
 * {
 *   terminal: {...}
 * }
 *
 * or directly return the terminal object.
 */
function unwrap(
  payload: unknown,
): Record<string, unknown> {
  const root = record(payload);

  // ------------------------------------------------------------
  // Terminal-frontend contract shape:
  //   { contract_version, symbol, timeframe, context, sections, ui, controls, authority }
  // Each section: { section, selectors, data: { available, executed, result, error } }
  // ------------------------------------------------------------
  const isTerminalContract =
    typeof root.contract_version === "string" ||
    (isRecord(root.sections) && isRecord(root.context));

  if (isTerminalContract) {
    const sections = record(root.sections);
    const context = record(root.context);

    const ctxMarket = record(context.market);
    const ctxSnap = record(ctxMarket.snapshot);

    const decisionSection = record(sections.decision);
    const intelligenceSection = record(sections.intelligence);
    const evidenceSection = record(sections.evidence);
    const riskSection = record(sections.risk);
    const casSection = record(sections.cas);
    const marketSection = record(sections.market);

    const decisionResult = record(record(decisionSection.data).result);
    const intelligenceResult = record(record(intelligenceSection.data).result);
    const evidenceResult = record(record(evidenceSection.data).result);
    const riskResult = record(record(riskSection.data).result);
    const casResult = record(record(casSection.data).result);

    // Prefer market snapshot from sections.market if present, else context
    const marketSnapRaw = record(record(marketSection.data).snapshot);
    const marketSnap =
      Object.keys(marketSnapRaw).length > 0 ? marketSnapRaw : ctxSnap;

    const snapMarket = record(marketSnap.market);
    const snapInstrument = record(marketSnap.instrument);
    const snapVenue = record(marketSnap.venue);
    const observation = record(marketSnap.observation);
    const snapState = record(marketSnap.state);

    const symbolValue = first(
      snapInstrument.symbol,
      context.symbol,
      root.symbol,
    );

    const priceValue = first(observation.price, null);

    const instrument = {
      symbol: symbolValue,
      market: snapMarket.market,
      segment: snapMarket.segment,
      venue: snapVenue.venue,
      country: snapMarket.country,
      instrumentType: first(
        snapInstrument.instrument_type,
        snapInstrument.instrumentType,
      ),
      price: priceValue,
      changePercent: first(
        observation.change_percent,
        observation.changePercent,
      ),
      liveState: first(snapState.session, marketSnap.state),
    };

    const decision = {
      ...decisionResult,
      decision: first(
        decisionResult.decision,
        decisionResult.direction,
        intelligenceResult.directional_bias,
        "HOLD",
      ),
      direction: first(
        decisionResult.direction,
        intelligenceResult.directional_bias,
      ),
      state: first(
        decisionResult.state,
        decisionResult.status,
        intelligenceResult.state,
      ),
      status: first(decisionResult.status, intelligenceResult.state),
      ready: first(decisionResult.ready, decisionResult.approved),
      reason: first(
        decisionResult.reason,
        Array.isArray(decisionResult.gate_reasons)
          ? decisionResult.gate_reasons[0]
          : undefined,
      ),
      message: decisionResult.message,
    };

    const intelligence = {
      ...intelligenceResult,
      state: first(intelligenceResult.state, intelligenceResult.status),
      score: first(
        intelligenceResult.intelligence_score,
        intelligenceResult.score,
      ),
      direction: first(
        intelligenceResult.directional_bias,
        intelligenceResult.direction,
      ),
    };

    return {
      symbol: symbolValue,
      timeframe: first(context.timeframe, root.timeframe),
      instrument,
      decision,
      intelligence,
      evidence: (() => {
        const norm = record(evidenceResult.normalized);
        const conf = record(evidenceResult.conflict_result);
        const rel = record(evidenceResult.reliability_results);
        const pkg = record(evidenceResult.package);
        const supporting = numberOrNull(norm.normalized_count);
        const conflicting = numberOrNull(conf.conflict_count);
        const relKeys = Object.keys(rel);
        const provenance = relKeys.length > 0 ? relKeys.join(", ") : undefined;
        const temporal = stringOrUndefined(pkg.created_at);
        return {
          ...evidenceResult,
          state: first(evidenceResult.status, evidenceResult.state),
          status: evidenceResult.status,
          supportingCount: supporting ?? undefined,
          conflictingCount: conflicting ?? undefined,
          acceptedCount: numberOrNull(evidenceResult.accepted_count) ?? undefined,
          rejectedCount: numberOrNull(evidenceResult.rejected_count) ?? undefined,
          provenance,
          temporal,
        };
      })(),
      risk: riskResult,
      cas: casResult,
      _raw: root,
    };
  }

  // ------------------------------------------------------------
  // Legacy unwrap (backward compat)
  // ------------------------------------------------------------
  const candidates = [
    root.research,
    root.intelligence,
    root.terminal,
    root.data,
    root.result,
    root.state,
  ];

  for (const candidate of candidates) {
    if (isRecord(candidate)) {
      return candidate;
    }
  }

  return root;
}

function normalizeInstrument(
  root: Record<string, unknown>,
): ResearchInstrument {
  const source = record(root.instrument);

  return {
    symbol: stringOrUndefined(
      first(
        source.symbol,
        root.symbol,
        source.instrument,
      ),
    ),

    market: stringOrUndefined(
      first(
        source.market,
        root.market,
      ),
    ),

    segment: stringOrUndefined(
      first(
        source.segment,
        root.segment,
      ),
    ),

    venue: stringOrUndefined(
      first(
        source.venue,
        root.venue,
      ),
    ),

    country: stringOrUndefined(
      first(
        source.country,
        root.country,
      ),
    ),

    instrumentType: stringOrUndefined(
      first(
        source.instrumentType,
        source.instrument_type,
        root.instrumentType,
        root.instrument_type,
      ),
    ),

    price: numberOrNull(
      first(
        source.price,
        source.currentPrice,
        root.price,
        root.currentPrice,
      ),
    ),

    changePercent: numberOrNull(
      first(
        source.changePercent,
        source.change_percent,
        root.changePercent,
        root.change_percent,
      ),
    ),

    liveState: stringOrUndefined(
      first(
        source.liveState,
        source.live_state,
        root.liveState,
        root.live_state,
      ),
    ),
  };
}

function normalizeDecisionState(
  root: Record<string, unknown>,
): ResearchDecision {
  const source = record(root.decision);

  return {
    decision: normalizeDecision(
      first(
        source.decision,
        source.action,
        root.decisionState,
        root.decision_state,
        root.decision,
      ),
    ),

    direction: stringOrUndefined(
      first(
        source.direction,
        root.direction,
      ),
    ),

    score: numberOrNull(
      first(
        source.score,
        source.decisionScore,
        source.decision_score,
        root.decisionScore,
        root.decision_score,
      ),
    ),

    grade: stringOrUndefined(
      first(
        source.grade,
        source.qualityGrade,
        source.quality_grade,
        root.grade,
        root.qualityGrade,
        root.quality_grade,
      ),
    ),

    state: stringOrUndefined(
      first(
        source.state,
        source.status,
      ),
    ),

    status: stringOrUndefined(
      source.status,
    ),

    ready: booleanOrUndefined(
      first(
        source.ready,
        source.decisionReady,
        source.decision_ready,
      ),
    ),

    reason: stringOrUndefined(
      first(
        source.reason,
        source.rationale,
      ),
    ),

    message: stringOrUndefined(
      source.message,
    ),
  };
}

function normalizeEngine(
  value: unknown,
  index: number,
): ResearchEngine {
  const source = record(value);

  const name =
    stringOrUndefined(
      first(
        source.name,
        source.engine,
        source.engineName,
        source.engine_name,
        source.code,
        source.id,
      ),
    ) ?? `ENGINE-${index + 1}`;

  return {
    id:
      stringOrUndefined(
        source.id,
      ) ?? name,

    name,

    shortName:
      stringOrUndefined(
        first(
          source.shortName,
          source.short_name,
          source.code,
          name,
        ),
      ) ?? name,

    score: numberOrNull(
      first(
        source.score,
        source.value,
        source.normalizedScore,
        source.normalized_score,
      ),
    ),

    grade: stringOrUndefined(
      first(
        source.grade,
        source.qualityGrade,
        source.quality_grade,
      ),
    ),

    state: stringOrUndefined(
      first(
        source.state,
        source.status,
        source.context,
      ),
    ),

    direction: stringOrUndefined(
      first(
        source.direction,
        source.bias,
      ),
    ),

    status: stringOrUndefined(
      source.status,
    ),

    message: stringOrUndefined(
      source.message,
    ),

    reason: stringOrUndefined(
      source.reason,
    ),

    source: stringOrUndefined(
      source.source,
    ),

    timestamp: stringOrUndefined(
      first(
        source.timestamp,
        source.asOf,
        source.as_of,
      ),
    ),
  };
}

function normalizeEngines(
  root: Record<string, unknown>,
): ResearchEngine[] {
  const intelligence =
    record(root.intelligence);

  const raw = first(
    root.engines,
    root.engineStrip,
    root.engine_strip,
    intelligence.engines,
    intelligence.items,
    root.intelligenceItems,
    root.intelligence_items,
  );

  if (Array.isArray(raw)) {
    return raw.map(normalizeEngine);
  }

  /*
   * Object form:
   *
   * {
   *   engines: {
   *     EQE: {...},
   *     MCT: {...}
   *   }
   * }
   */
  if (isRecord(raw)) {
    return Object.entries(raw).map(
      ([key, value], index) => {
        const item = normalizeEngine(
          value,
          index,
        );

        return {
          ...item,
          id: item.id || key,
          name: item.name || key,
          shortName:
            item.shortName || key,
        };
      },
    );
  }

  return [];
}

function normalizeStages(
  root: Record<string, unknown>,
): ResearchStage[] {
  const raw = first(
    root.stages,
    root.decisionStages,
    root.decision_stages,
    record(root.intelligence).stages,
  );

  if (Array.isArray(raw)) {
    return raw.map(
      (value, index) => {
        const source = record(value);

        const id =
          stringOrUndefined(
            first(
              source.id,
              source.stage,
              source.name,
            ),
          ) ?? `D${index + 1}`;

        return {
          id,

          label:
            stringOrUndefined(
              first(
                source.label,
                source.name,
                source.stage,
              ),
            ) ?? id,

          state: normalizeStage(
            first(
              source.state,
              source.status,
            ),
          ),

          message:
            stringOrUndefined(
              source.message,
            ),
        };
      },
    );
  }

  if (isRecord(raw)) {
    return Object.entries(raw).map(
      ([key, value]) => {
        const source = record(value);

        return {
          id: key,

          label:
            stringOrUndefined(
              first(
                source.label,
                source.name,
              ),
            ) ?? key,

          state: normalizeStage(
            first(
              source.state,
              source.status,
              value,
            ),
          ),

          message:
            stringOrUndefined(
              source.message,
            ),
        };
      },
    );
  }

  return [];
}

function normalizeEvidence(
  root: Record<string, unknown>,
): ResearchEvidenceState {
  const source = record(root.evidence);

  const rawItems = first(
    source.items,
    source.evidence,
    root.evidenceItems,
    root.evidence_items,
  );

  const items = array(rawItems).map(
    (value, index): ResearchEvidence => {
      const item = record(value);

      return {
        id:
          stringOrUndefined(
            first(
              item.id,
              item.evidenceId,
              item.evidence_id,
            ),
          ) ?? `EV-${index + 1}`,

        source:
          stringOrUndefined(
            item.source,
          ),

        dimension:
          stringOrUndefined(
            item.dimension,
          ),

        value: item.value,

        disposition:
          stringOrUndefined(
            item.disposition,
          ),

        validity:
          stringOrUndefined(
            item.validity,
          ),

        reason:
          stringOrUndefined(
            item.reason,
          ),

        observedAt:
          stringOrUndefined(
            first(
              item.observedAt,
              item.observed_at,
              item.asOf,
              item.as_of,
            ),
          ),
      };
    },
  );

  return {
    state:
      stringOrUndefined(
        first(
          source.state,
          source.status,
        ),
      ),

    status:
      stringOrUndefined(
        source.status,
      ),

    packageState:
      stringOrUndefined(
        first(
          source.packageState,
          source.package_state,
        ),
      ),

    supportingCount:
      numberOrNull(
        first(
          source.supportingCount,
          source.supporting_count,
        ),
      ) ?? undefined,

    conflictingCount:
      numberOrNull(
        first(
          source.conflictingCount,
          source.conflicting_count,
        ),
      ) ?? undefined,

    acceptedCount:
      numberOrNull(
        first(
          source.acceptedCount,
          source.accepted_count,
        ),
      ) ?? undefined,

    rejectedCount:
      numberOrNull(
        first(
          source.rejectedCount,
          source.rejected_count,
        ),
      ) ?? undefined,

    provenance:
      stringOrUndefined(
        source.provenance,
      ),

    temporal:
      stringOrUndefined(
        first(
          source.temporal,
          source.temporalValidation,
          source.temporal_validation,
        ),
      ),

    items,
  };
}

function normalizeContradictions(
  root: Record<string, unknown>,
): ResearchContradiction[] {
  const intelligence =
    record(root.intelligence);

  const raw = first(
    root.contradictions,
    intelligence.contradictions,
  );

  return array(raw).map(
    (value, index) => {
      const item = record(value);

      return {
        id:
          stringOrUndefined(
            first(
              item.id,
              item.conflictId,
              item.conflict_id,
              item.type,
            ),
          ) ?? `CON-${index + 1}`,

        type:
          stringOrUndefined(
            item.type,
          ),

        severity:
          stringOrUndefined(
            item.severity,
          ),

        state:
          stringOrUndefined(
            item.state,
          ),

        message:
          stringOrUndefined(
            first(
              item.message,
              item.reason,
            ),
          ),

        resolution:
          stringOrUndefined(
            item.resolution,
          ),

        source:
          stringOrUndefined(
            item.source,
          ),
      };
    },
  );
}

function normalizeDecisionMap(
  root: Record<string, unknown>,
): ResearchDecisionMap {
  const source = record(
    first(
      root.decisionMap,
      root.decision_map,
    ),
  );

  return {
    marketState:
      stringOrUndefined(
        first(
          source.marketState,
          source.market_state,
          root.marketState,
          root.market_state,
        ),
      ),

    transition:
      stringOrUndefined(
        first(
          source.transition,
          source.transitionType,
          source.transition_type,
          root.transition,
          root.transitionType,
          root.transition_type,
        ),
      ),

    scenario:
      stringOrUndefined(
        first(
          source.scenario,
          source.scenarioType,
          source.scenario_type,
          root.scenario,
          root.scenarioType,
          root.scenario_type,
        ),
      ),

    direction:
      stringOrUndefined(
        first(
          source.direction,
          root.direction,
        ),
      ),

    structure:
      stringOrUndefined(
        first(
          source.structure,
          root.structure,
        ),
      ),

    liquidity:
      stringOrUndefined(
        first(
          source.liquidity,
          root.liquidity,
        ),
      ),

    accumulation:
      stringOrUndefined(
        first(
          source.accumulation,
          root.accumulation,
        ),
      ),

    distribution:
      stringOrUndefined(
        first(
          source.distribution,
          root.distribution,
        ),
      ),

    volatility:
      stringOrUndefined(
        first(
          source.volatility,
          root.volatility,
        ),
      ),

    timing:
      stringOrUndefined(
        first(
          source.timing,
          root.timing,
        ),
      ),

    regime:
      stringOrUndefined(
        first(
          source.regime,
          root.regime,
        ),
      ),
  };
}

function normalizeTradeAuthority(
  root: Record<string, unknown>,
): ResearchTradeAuthority {
  const source = record(
    first(
      root.tradeAuthority,
      root.trade_authority,
    ),
  );

  const auto = record(source.auto);
  const manual = record(source.manual);
  const policy = record(
    source.userPolicy,
  );

  const actions = record(
    source.actions,
  );

  const normalizeAction = (
    value: unknown,
  ): ResearchAction => {
    const action = record(value);

    return {
      state: normalizeAuthority(
        action.state,
      ),

      enabled:
        booleanOrUndefined(
          action.enabled,
        ),

      reason:
        stringOrUndefined(
          action.reason,
        ),

      message:
        stringOrUndefined(
          action.message,
        ),
    };
  };

  return {
    userPolicy: {
      enabled:
        booleanOrUndefined(
          policy.enabled,
        ),

      minimumScore:
        numberOrNull(
          first(
            policy.minimumScore,
            policy.minimum_score,
          ),
        ),

      belowMinimumAction:
        normalizeDecision(
          first(
            policy.belowMinimumAction,
            policy.below_minimum_action,
          ),
        ),

      description:
        stringOrUndefined(
          policy.description,
        ),
    },

    auto: {
      state: normalizeAuthority(
        auto.state,
      ),

      decision: normalizeDecision(
        auto.decision,
      ),

      enabled:
        booleanOrUndefined(
          auto.enabled,
        ),

      reason:
        stringOrUndefined(
          auto.reason,
        ),

      message:
        stringOrUndefined(
          auto.message,
        ),
    },

    manual: {
      state: normalizeAuthority(
        manual.state,
      ),

      decision: normalizeDecision(
        manual.decision,
      ),

      enabled:
        booleanOrUndefined(
          manual.enabled,
        ),

      reason:
        stringOrUndefined(
          manual.reason,
        ),

      message:
        stringOrUndefined(
          manual.message,
        ),
    },

    actions: {
      buy: normalizeAction(
        actions.buy,
      ),

      sell: normalizeAction(
        actions.sell,
      ),

      hold: normalizeAction(
        actions.hold,
      ),

      wait: normalizeAction(
        actions.wait,
      ),
    },
  };
}

function normalizeScenarios(
  root: Record<string, unknown>,
): ResearchScenarios[] {
  const intelligence =
    record(root.intelligence);

  const raw = first(
    root.scenarios,
    root.futureScenarios,
    root.future_scenarios,
    intelligence.scenarios,
  );

  return array(raw).map(
    (value) => {
      const item = record(value);

      return {
        id:
          stringOrUndefined(
            item.id,
          ),

        type:
          stringOrUndefined(
            first(
              item.type,
              item.scenarioType,
              item.scenario_type,
            ),
          ),

        direction:
          stringOrUndefined(
            item.direction,
          ),

        state:
          stringOrUndefined(
            item.state,
          ),

        description:
          stringOrUndefined(
            first(
              item.description,
              item.statement,
              item.reason,
            ),
          ),

        invalidation:
          stringOrUndefined(
            item.invalidation,
          ),
      };
    },
  );
}

function normalizeSystem(
  root: Record<string, unknown>,
): ResearchSystemState {
  const source = record(root.system);

  return {
    marketData:
      stringOrUndefined(
        first(
          source.marketData,
          source.market_data,
        ),
      ),

    evidence:
      stringOrUndefined(
        source.evidence,
      ),

    intelligence:
      stringOrUndefined(
        source.intelligence,
      ),

    risk:
      stringOrUndefined(
        source.risk,
      ),

    execution:
      stringOrUndefined(
        source.execution,
      ),

    cas:
      stringOrUndefined(
        source.cas,
      ),
  };
}

function normalizeResearch(
  payload: unknown,
): ResearchApiState {
  const root = unwrap(payload);

  const rawIntelligence =
    record(root.intelligence);

  const engines =
    normalizeEngines(root);

  const intelligenceItems =
    engines.length > 0
      ? engines
      : array(
          first(
            rawIntelligence.items,
            rawIntelligence.engines,
          ),
        ).map(normalizeEngine);

  const state: ResearchApiState = {
    requestId:
      stringOrUndefined(
        first(
          root.requestId,
          root.request_id,
        ),
      ),

    generatedAt:
      stringOrUndefined(
        first(
          root.generatedAt,
          root.generated_at,
          root.asOf,
          root.as_of,
        ),
      ),

    instrument:
      normalizeInstrument(root),

    decision:
      normalizeDecisionState(root),

    intelligence: {
      state:
        stringOrUndefined(
          first(
            rawIntelligence.state,
            rawIntelligence.status,
          ),
        ),

      score:
        numberOrNull(
          first(
            rawIntelligence.score,
            rawIntelligence.intelligenceScore,
            rawIntelligence.intelligence_score,
          ),
        ),

      grade:
        stringOrUndefined(
          first(
            rawIntelligence.grade,
            rawIntelligence.qualityGrade,
            rawIntelligence.quality_grade,
          ),
        ),

      direction:
        stringOrUndefined(
          rawIntelligence.direction,
        ),

      items: intelligenceItems,

      contradictions:
        normalizeContradictions(root),
    },

    engines,

    stages:
      normalizeStages(root),

    decisionMap:
      normalizeDecisionMap(root),

    evidence:
      normalizeEvidence(root),

    contradictions:
      normalizeContradictions(root),

    tradeAuthority:
      normalizeTradeAuthority(root),

    scenarios:
      normalizeScenarios(root),

    system:
      normalizeSystem(root),

    raw: payload,
  };

  // ---- Derived fallback for missing backend sections ----
  if (state.stages.length === 0) {
    state.stages = deriveStages(root);
  }
  if (state.engines.length === 0) {
    state.engines = deriveEngines(root);
  }
  const dmValues = Object.values(state.decisionMap);
  if (dmValues.every((v) => v === undefined || v === null)) {
    state.decisionMap = deriveDecisionMap(root);
  }

  return state;
}

// ============================================================
// DERIVED LAYER BUILDERS (v4)
// ------------------------------------------------------------
// Reads /api/terminal/frontend pipeline output and maps it to
// stages/engines/decision_map shapes. Only fields that ARE
// present in the backend response are used. Missing fields stay
// UNAVAILABLE. Nothing is fabricated.
// ============================================================

function _pickNum(...vals: unknown[]): number | null {
  for (const v of vals) {
    if (v === null || v === undefined) continue;
    if (typeof v === "number" && Number.isFinite(v)) return v;
    if (typeof v === "string" && v.trim() !== "") {
      const n = Number(v);
      if (Number.isFinite(n)) return n;
    }
  }
  return null;
}

function deriveStages(
  root: Record<string, unknown>,
): ResearchStage[] {
  const decision = record(root.decision);
  const intelligence = record(root.intelligence);
  const evidence = record(root.evidence);
  const instrument = record(root.instrument);

  const raw = record(root._raw);
  const context = record(raw.context);
  const snapshot = record(record(context.market).snapshot);
  const observation = record(snapshot.observation);
  const snapState = record(snapshot.state);
  const conflict = record(evidence.conflict_result);
  const normalized = record(evidence.normalized);

  const evidenceOk = Boolean(evidence.package || evidence.status);
  const intelScore = _pickNum(intelligence.intelligence_score, intelligence.score) ?? 0;
  const decisionScore = _pickNum(decision.decision_score) ?? 0;
  const confidence = _pickNum(decision.confidence) ?? 0;
  const approved = Boolean(decision.approved);
  const conflicts = _pickNum(conflict.conflict_count) ?? 0;
  const session = stringOrUndefined(snapState.session);
  const marketName = stringOrUndefined(instrument.market);
  const instrType = stringOrUndefined(instrument.instrumentType);

  const highP = _pickNum(observation.high);
  const lowP = _pickNum(observation.low);
  const priceP = _pickNum(observation.price);
  const volatility =
    highP !== null && lowP !== null && priceP !== null && priceP !== 0
      ? ((highP - lowP) / priceP) * 100
      : null;

  const gateReasons = Array.isArray(decision.gate_reasons)
    ? (decision.gate_reasons as unknown[]).map(String)
    : [];
  const intelReasons = Array.isArray(intelligence.reasons)
    ? (intelligence.reasons as unknown[]).map(String)
    : [];

  const confidenceMsg =
    confidence > 0
      ? `Confidence: ${confidence.toFixed(2)}`
      : (gateReasons.find((r) => /confidence/i.test(r)) ?? "Confidence pending");

  const intelMsg =
    intelScore > 0
      ? `Score: ${intelScore.toFixed(2)}`
      : (intelReasons[0] ?? "Intelligence pending");

  const normCount = _pickNum(normalized.normalized_count) ?? 0;

  const mk = (
    id: string,
    label: string,
    state: ResearchStage["state"],
    message?: string,
  ): ResearchStage => ({ id, label, state, message });

  return [
    mk("D1", "Readiness", evidenceOk ? "ACTIVE" : "PENDING",
       evidenceOk ? `Evidence package: ${normCount} item(s)` : "Awaiting evidence"),
    mk("D2", "Condition", session === "open" ? "ACTIVE" : "PENDING",
       session ?? "Session unknown"),
    mk("D3", "Confidence", confidence > 0 ? "ACTIVE" : "PENDING", confidenceMsg),
    mk("D4", "Relationships", conflicts > 0 ? "REVIEW" : "PASS",
       `Conflicts: ${conflicts}`),
    mk("D5", "Structure", "UNAVAILABLE", "Not in backend pipeline"),
    mk("D6", "Flow", "UNAVAILABLE", "Not in backend pipeline"),
    mk("D7", "Liquidity / Volatility",
       volatility !== null ? "ACTIVE" : "UNAVAILABLE",
       volatility !== null
         ? `Range: ${volatility.toFixed(2)}%`
         : "No snapshot"),
    mk("D8", "Instrument", instrType ? "ACTIVE" : "PENDING",
       instrType ?? "Instrument type unknown"),
    mk("D9", "Time / Event", "ACTIVE",
       stringOrUndefined(root.timeframe) ?? "1m"),
    mk("D10", "Market State", marketName ? "ACTIVE" : "PENDING",
       marketName ?? "Market unknown"),
    mk("D11", "Transition", "UNAVAILABLE", "Not in backend pipeline"),
    mk("D12", "Future Scenario", "UNAVAILABLE", "Not in backend pipeline"),
    mk("D13", "Decision", "ACTIVE",
       `${stringOrUndefined(decision.direction) ?? "HOLD"} @ ${decisionScore.toFixed(2)}`),
    mk("D14", "Validation", approved ? "PASS" : "REVIEW",
       approved ? "Approved" : (gateReasons[0] ?? "Not approved")),
    mk("D15", "Learning", "UNAVAILABLE", "Not in backend pipeline"),
    mk("D16", "Intelligence",
       intelScore > 0 ? "ACTIVE" : "PENDING",
       intelMsg),
  ];
}

function deriveEngines(
  root: Record<string, unknown>,
): ResearchEngine[] {
  const decision = record(root.decision);
  const evidence = record(root.evidence);
  const risk = record(root.risk);
  const cas = record(root.cas);
  const intelligence = record(root.intelligence);
  const instrument = record(root.instrument);

  const raw = record(root._raw);
  const context = record(raw.context);
  const snapshot = record(record(context.market).snapshot);
  const observation = record(snapshot.observation);
  const conflict = record(evidence.conflict_result);
  const normalized = record(evidence.normalized);
  const reliability = record(evidence.reliability_results);

  const evidenceStatus = stringOrUndefined(evidence.status);
  const riskResult = record(risk.result);
  const riskStatus = stringOrUndefined(riskResult.status);
  const riskScore = _pickNum(riskResult.risk_score, decision.risk_score);
  const casResult = record(cas.result);
  const casStatus = stringOrUndefined(casResult.status);
  const casGates = Array.isArray(casResult.gates_executed)
    ? (casResult.gates_executed as unknown[]).length
    : null;

  const conflicts = _pickNum(conflict.conflict_count) ?? 0;
  const comparable = _pickNum(conflict.comparable_count);
  const analyzed = _pickNum(conflict.analyzed_count);
  const normCount = _pickNum(normalized.normalized_count) ?? 0;
  const rejectCount = _pickNum(evidence.rejected_count) ?? 0;

  const timingScore = _pickNum(decision.timing_score);
  const contextScore = _pickNum(intelligence.context_score);
  const volume = _pickNum(observation.volume);
  const binanceRel = record(reliability.binance);
  const reliabilityStatus = stringOrUndefined(binanceRel.status);

  const mk = (
    id: string,
    name: string,
    state: string,
    score: number | null,
    message?: string,
  ): ResearchEngine => ({
    id, name, shortName: id,
    state, status: state,
    score, message,
  });

  return [
    mk("EQE", "Evidence Quality",
       evidenceStatus === "VALID" ? "ACTIVE" : "PENDING",
       normCount > 0 ? normCount : null,
       `${normCount} accepted, ${rejectCount} rejected${reliabilityStatus ? `, source: ${reliabilityStatus}` : ""}`),
    mk("MCT", "Market Context",
       instrument.market ? "ACTIVE" : "PENDING",
       contextScore,
       stringOrUndefined(instrument.market) ?? "no context"),
    mk("LQS", "Liquidity Score",
       volume !== null ? "ACTIVE" : "UNAVAILABLE",
       volume,
       volume !== null ? "volume" : "no snapshot"),
    mk("MTS", "Market Timing",
       timingScore !== null ? "ACTIVE" : "PENDING",
       timingScore,
       timingScore !== null ? "decision timing_score" : "no timing data"),
    mk("REL", "Relationships",
       conflicts > 0 ? "REVIEW" : "PASS",
       comparable ?? analyzed ?? null,
       `conflicts: ${conflicts}`),
    mk("REG", "Regime",
       instrument.market ? "ACTIVE" : "UNAVAILABLE",
       null,
       stringOrUndefined(instrument.market) ?? "unknown"),
    mk("MAG", "Magnitude",
       volume !== null ? "ACTIVE" : "UNAVAILABLE",
       volume,
       volume !== null ? "24h volume" : "no volume"),
    mk("STR", "Structure", "UNAVAILABLE", null, "Not in backend pipeline"),
    mk("RSK", "Risk",
       riskStatus ? "ACTIVE" : "PENDING",
       riskScore,
       riskStatus ?? "no risk result"),
    mk("CAS", "CAS",
       casStatus ? "ACTIVE" : "PENDING",
       casGates,
       casStatus ?? "no CAS result"),
  ];
}

function deriveDecisionMap(
  root: Record<string, unknown>,
): ResearchDecisionMap {
  const decision = record(root.decision);
  const intelligence = record(root.intelligence);
  const instrument = record(root.instrument);

  const raw = record(root._raw);
  const context = record(raw.context);
  const snapshot = record(record(context.market).snapshot);
  const observation = record(snapshot.observation);

  const highP = _pickNum(observation.high);
  const lowP = _pickNum(observation.low);
  const priceP = _pickNum(observation.price);

  const volatility =
    highP !== null && lowP !== null && priceP !== null && priceP !== 0
      ? `${(((highP - lowP) / priceP) * 100).toFixed(2)}%`
      : undefined;

  const timingScore = _pickNum(decision.timing_score);
  const volume = _pickNum(observation.volume);

  return {
    marketState: stringOrUndefined(intelligence.state),
    transition: undefined,
    scenario: undefined,
    direction: stringOrUndefined(decision.direction),
    structure: undefined,
    liquidity: volume !== null ? String(volume) : undefined,
    accumulation: undefined,
    distribution: undefined,
    volatility,
    timing: timingScore !== null ? timingScore.toFixed(2) : undefined,
    regime: stringOrUndefined(instrument.market),
  };
}

function parseApiError(
  payload: unknown,
  status: number,
): ResearchApiError {
  const root = unwrap(payload);
  const error = record(root.error);

  return {
    code:
      stringOrUndefined(
        error.code,
      ) ?? `HTTP_${status}`,

    message:
      stringOrUndefined(
        error.message,
      ) ??
      `Research backend returned HTTP ${status}.`,

    retryable:
      typeof error.retryable === "boolean"
        ? error.retryable
        : status >= 500,

    requestId:
      stringOrUndefined(
        error.requestId,
      ),
  };
}

/**
 * Fetch the authoritative Research / Intelligence state.
 *
 * The backend endpoint is kept in one place so the page itself
 * does not contain transport logic.
 */
const DEFAULT_RESEARCH_SYMBOL = "BTCUSDT";

export async function getResearch(
  signal?: AbortSignal,
  symbol: string = DEFAULT_RESEARCH_SYMBOL,
): Promise<ResearchApiState> {
  let response: Response;

  const safeSymbol =
    (symbol && symbol.trim()) || DEFAULT_RESEARCH_SYMBOL;

  const requestUrl =
    `${RESEARCH_ENDPOINT}?symbol=${encodeURIComponent(safeSymbol)}`;

  try {
    response = await fetch(
      requestUrl,
      {
        method: "GET",

        headers: {
          Accept:
            "application/json",
        },

        cache: "no-store",

        signal,
      },
    );
  } catch (error) {
    if (
      error instanceof DOMException &&
      error.name === "AbortError"
    ) {
      throw error;
    }

    throw new ResearchApiException({
      code: "NETWORK_ERROR",
      message:
        "Unable to reach the ROBOMLM_PLUS backend.",
      retryable: true,
    });
  }

  let payload: unknown = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new ResearchApiException(
      parseApiError(
        payload,
        response.status,
      ),
    );
  }

  return normalizeResearch(
    payload,
  );
}

/**
 * Convenience polling helper.
 *
 * It intentionally returns the complete backend snapshot.
 * It does not patch individual UI fields or synthesize state.
 */
export function createResearchPoller(
  callback: (
    state: ResearchApiState,
  ) => void,
  onError?: (
    error: unknown,
  ) => void,
  intervalMs = 5000,
): () => void {
  let stopped = false;
  let timer: number | undefined;

  const poll = async () => {
    if (stopped) {
      return;
    }

    try {
      const state =
        await getResearch();

      if (!stopped) {
        callback(state);
      }
    } catch (error) {
      if (!stopped) {
        onError?.(error);
      }
    } finally {
      if (!stopped) {
        timer = window.setTimeout(
          poll,
          intervalMs,
        );
      }
    }
  };

  void poll();

  return () => {
    stopped = true;

    if (timer !== undefined) {
      window.clearTimeout(timer);
    }
  };
}

/**
 * Type guard useful to pages/components that receive
 * unknown backend payloads.
 */
export function isResearchApiState(
  value: unknown,
): value is ResearchApiState {
  if (!isRecord(value)) {
    return false;
  }

  return (
    "instrument" in value &&
    "decision" in value &&
    "intelligence" in value &&
    "engines" in value
  );
}

export default getResearch;
