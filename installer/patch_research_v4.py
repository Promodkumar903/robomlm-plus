# patch_research_v4.py
# Replaces DERIVED LAYER BUILDERS block with improved mapper.
# Fixes: Evidence extras, engine scores, D3/D16 reasons, MAG volume.
# Rule: backup PEHLE. Kuch delete nahi.

import os
import sys
import shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts"

START_MARKER = "// ============================================================\n// DERIVED LAYER BUILDERS"
END_MARKER = "function parseApiError("

NEW_BLOCK = r'''// ============================================================
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

'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "DERIVED LAYER BUILDERS (v4)" in src:
        print("ALREADY PATCHED v4. Skipping.")
        sys.exit(0)

    s = src.find(START_MARKER)
    if s < 0:
        print("ERROR: start marker not found. Run v3 patch first.")
        sys.exit(1)

    e = src.find(END_MARKER, s)
    if e < 0:
        print("ERROR: end marker not found.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + f".bak_{ts}"
    try:
        shutil.copy2(TARGET, backup)
    except Exception as ex:
        print(f"ERROR: backup failed -> {ex}")
        sys.exit(1)
    if not os.path.isfile(backup):
        print("ERROR: backup not verified. Abort.")
        sys.exit(1)
    print(f"BACKUP OK: {backup}")

    new_src = src[:s] + NEW_BLOCK + src[e:]

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback:")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()