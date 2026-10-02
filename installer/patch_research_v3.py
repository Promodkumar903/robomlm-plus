# patch_research_v3.py
# Adds derived D1-D16 stages, engines, decision_map to research.ts
# Derives from pipeline data already present in /api/terminal/frontend response.
# Rule: backup PEHLE. Kuch delete nahi.

import os
import sys
import shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts"

DERIVE_BLOCK = r'''// ============================================================
// DERIVED LAYER BUILDERS
// ------------------------------------------------------------
// The backend /api/terminal/frontend response does NOT send
// stages, engines, or decision_map. We derive them here from
// pipeline outputs that ARE present (decision, intelligence,
// evidence, risk, cas, snapshot). This is clearly derived,
// not authoritative backend D1-D16 math.
// ============================================================

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

  const evidenceOk = Boolean(evidence.package || evidence.status);
  const intelScore =
    numberOrNull(intelligence.intelligence_score) ??
    numberOrNull(intelligence.score) ??
    0;
  const decisionScore = numberOrNull(decision.decision_score) ?? 0;
  const confidence = numberOrNull(decision.confidence) ?? 0;
  const approved = Boolean(decision.approved);
  const conflicts = numberOrNull(conflict.conflict_count) ?? 0;
  const session = stringOrUndefined(snapState.session);
  const marketName = stringOrUndefined(instrument.market);
  const instrType = stringOrUndefined(instrument.instrumentType);

  const highP = numberOrNull(observation.high);
  const lowP = numberOrNull(observation.low);
  const priceP = numberOrNull(observation.price);

  const volatility =
    highP !== null && lowP !== null && priceP !== null && priceP !== 0
      ? ((highP - lowP) / priceP) * 100
      : null;

  const mk = (
    id: string,
    label: string,
    state: ResearchStage["state"],
    message?: string,
  ): ResearchStage => ({ id, label, state, message });

  return [
    mk("D1", "Readiness", evidenceOk ? "ACTIVE" : "PENDING",
       evidenceOk ? "Evidence package available" : "Awaiting evidence"),
    mk("D2", "Condition", session === "open" ? "ACTIVE" : "PENDING",
       session ?? "Session unknown"),
    mk("D3", "Confidence", confidence > 0 ? "ACTIVE" : "PENDING",
       `Confidence: ${confidence.toFixed(2)}`),
    mk("D4", "Relationships", conflicts > 0 ? "REVIEW" : "PASS",
       `Conflicts: ${conflicts}`),
    mk("D5", "Structure", "UNAVAILABLE", "Not present in pipeline"),
    mk("D6", "Flow", "UNAVAILABLE", "Not present in pipeline"),
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
    mk("D11", "Transition", "UNAVAILABLE", "Not present in pipeline"),
    mk("D12", "Future Scenario", "UNAVAILABLE", "Not present in pipeline"),
    mk("D13", "Decision", "ACTIVE",
       `${stringOrUndefined(decision.direction) ?? "HOLD"} @ ${decisionScore.toFixed(2)}`),
    mk("D14", "Validation", approved ? "PASS" : "REVIEW",
       approved ? "Approved" : "Not approved"),
    mk("D15", "Learning", "UNAVAILABLE", "Not present in pipeline"),
    mk("D16", "Intelligence",
       intelScore > 0 ? "ACTIVE" : "PENDING",
       `Score: ${intelScore.toFixed(2)}`),
  ];
}

function deriveEngines(
  root: Record<string, unknown>,
): ResearchEngine[] {
  const decision = record(root.decision);
  const evidence = record(root.evidence);
  const risk = record(root.risk);
  const cas = record(root.cas);
  const instrument = record(root.instrument);

  const raw = record(root._raw);
  const context = record(raw.context);
  const snapshot = record(record(context.market).snapshot);
  const observation = record(snapshot.observation);
  const conflict = record(evidence.conflict_result);

  const evidenceStatus = stringOrUndefined(evidence.status);
  const riskStatus = stringOrUndefined(record(risk.result).status);
  const casStatus = stringOrUndefined(record(cas.result).status);
  const conflicts = numberOrNull(conflict.conflict_count) ?? 0;
  const timingScore = numberOrNull(decision.timing_score) ?? 0;
  const volume = numberOrNull(observation.volume);

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
       null, evidenceStatus ?? "No evidence"),
    mk("MCT", "Market Context",
       instrument.market ? "ACTIVE" : "PENDING",
       null, stringOrUndefined(instrument.market)),
    mk("LQS", "Liquidity Score",
       volume !== null ? "ACTIVE" : "UNAVAILABLE",
       volume),
    mk("MTS", "Market Timing",
       timingScore > 0 ? "ACTIVE" : "PENDING",
       timingScore),
    mk("REL", "Relationships",
       conflicts > 0 ? "REVIEW" : "PASS",
       null, `Conflicts: ${conflicts}`),
    mk("REG", "Regime",
       instrument.market ? "ACTIVE" : "UNAVAILABLE",
       null, stringOrUndefined(instrument.market)),
    mk("MAG", "Magnitude",
       volume !== null ? "ACTIVE" : "UNAVAILABLE", null),
    mk("STR", "Structure", "UNAVAILABLE", null, "Not in pipeline"),
    mk("RSK", "Risk",
       riskStatus ? "ACTIVE" : "PENDING",
       null, riskStatus ?? "No risk result"),
    mk("CAS", "CAS",
       casStatus ? "ACTIVE" : "PENDING",
       null, casStatus ?? "No CAS result"),
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

  const highP = numberOrNull(observation.high);
  const lowP = numberOrNull(observation.low);
  const priceP = numberOrNull(observation.price);

  const volatility =
    highP !== null && lowP !== null && priceP !== null && priceP !== 0
      ? `${(((highP - lowP) / priceP) * 100).toFixed(2)}%`
      : undefined;

  const timingScore = numberOrNull(decision.timing_score);

  return {
    marketState: stringOrUndefined(intelligence.state),
    transition: undefined,
    scenario: undefined,
    direction: stringOrUndefined(decision.direction),
    structure: undefined,
    liquidity: stringOrUndefined(observation.volume),
    accumulation: undefined,
    distribution: undefined,
    volatility,
    timing: timingScore !== null ? timingScore.toFixed(2) : undefined,
    regime: stringOrUndefined(instrument.market),
  };
}

'''

# Anchor to insert derive functions before parseApiError
INSERT_ANCHOR = "function parseApiError("

# Return statement change in normalizeResearch
RETURN_OPEN_OLD = "  return {\n    requestId:"
RETURN_OPEN_NEW = "  const state: ResearchApiState = {\n    requestId:"

RETURN_CLOSE_OLD = "    raw: payload,\n  };\n}"
RETURN_CLOSE_NEW = """    raw: payload,
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
}"""


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "DERIVED LAYER BUILDERS" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if "Terminal-frontend contract shape" not in src:
        print("ERROR: v2 patch not present. Run patch_research_v2.py first.")
        sys.exit(1)

    if INSERT_ANCHOR not in src:
        print(f"ERROR: anchor '{INSERT_ANCHOR}' not found.")
        sys.exit(1)

    if RETURN_OPEN_OLD not in src:
        print("ERROR: return-open anchor not found.")
        sys.exit(1)

    if RETURN_CLOSE_OLD not in src:
        print("ERROR: return-close anchor not found.")
        sys.exit(1)

    # ---- Backup FIRST ----
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + f".bak_{ts}"
    try:
        shutil.copy2(TARGET, backup)
    except Exception as e:
        print(f"ERROR: backup failed -> {e}")
        print("Backup ke bina edit nahi hoga. Abort.")
        sys.exit(1)

    if not os.path.isfile(backup):
        print("ERROR: backup not verified. Abort.")
        sys.exit(1)
    print(f"BACKUP OK: {backup}")

    # ---- Apply patches ----
    new_src = src

    # 1. Insert derive functions before parseApiError
    new_src = new_src.replace(
        INSERT_ANCHOR,
        DERIVE_BLOCK + INSERT_ANCHOR,
        1,
    )

    # 2. Change return-open
    new_src = new_src.replace(
        RETURN_OPEN_OLD,
        RETURN_OPEN_NEW,
        1,
    )

    # 3. Change return-close (add post-processing + return state)
    new_src = new_src.replace(
        RETURN_CLOSE_OLD,
        RETURN_CLOSE_NEW,
        1,
    )

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback (agar zaroorat pade):")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()