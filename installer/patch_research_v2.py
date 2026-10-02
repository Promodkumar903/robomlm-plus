# patch_research_v2.py
# Fix: Research page data blank despite backend returning full data.
# Reason: /api/terminal/frontend uses new contract shape (sections.*.data.result)
#         but unwrap() in research.ts only understands old shape.
#
# Rule: backup PEHLE, phir edit. Kuch delete nahi.

import os
import sys
import shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts"

NEW_UNWRAP = '''function unwrap(
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
      evidence: {
        ...evidenceResult,
        state: first(evidenceResult.status, evidenceResult.state),
        status: evidenceResult.status,
      },
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
'''


def find_function_span(src, start_marker):
    """Return (start, end) span of a top-level function body."""
    start = src.find(start_marker)
    if start < 0:
        return None
    brace = src.find("{", start)
    if brace < 0:
        return None
    depth = 1
    i = brace + 1
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    if depth != 0:
        return None
    end = i
    if end < len(src) and src[end] == "\n":
        end += 1
    return (start, end)


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "Terminal-frontend contract shape" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    span = find_function_span(src, "function unwrap(")
    if not span:
        print("ERROR: cannot locate unwrap() function. Abort.")
        sys.exit(1)

    start, end = span

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

    # ---- Replace ----
    new_src = src[:start] + NEW_UNWRAP + src[end:]

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback (agar zaroorat pade):")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()