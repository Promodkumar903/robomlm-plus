import type {
  EvidenceItem,
  DecisionPanelData,
  RiskPanelData
} from "../ui";

function isRecord(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null
  );
}

/**
 * Copies only fields that actually exist on the
 * backend object. It never creates missing values.
 */
function copyExistingFields<T extends object>(
  source: Record<string, unknown>,
  keys: readonly (keyof T)[]
): Partial<T> {
  const result: Partial<T> = {};

  for (const key of keys) {
    if (
      Object.prototype.hasOwnProperty.call(
        source,
        key
      )
    ) {
      result[key] =
        source[String(key)] as T[typeof key];
    }
  }

  return result;
}

const evidenceKeys = [
  "id",
  "source",
  "title",
  "claim",
  "timestamp",
  "confidence",
  "status"
] as const satisfies readonly (keyof EvidenceItem)[];

const decisionKeys = [
  "decision",
  "action",
  "rationale",
  "confidence",
  "timestamp",
  "evidenceIds"
] as const satisfies readonly (
  keyof DecisionPanelData
)[];

const riskKeys = [
  "level",
  "status",
  "summary",
  "exposure",
  "maxLoss",
  "warnings",
  "gates"
] as const satisfies readonly (
  keyof RiskPanelData
)[];

/**
 * Adapts one already-existing backend evidence object.
 *
 * No defaults are invented.
 * Missing backend fields remain missing.
 */
export function toEvidenceItem(
  source: unknown
): EvidenceItem | null {
  if (!isRecord(source)) {
    return null;
  }

  return copyExistingFields<EvidenceItem>(
    source,
    evidenceKeys
  ) as EvidenceItem;
}

/**
 * Adapts an evidence payload only when the payload
 * itself is an array.
 *
 * We deliberately do not assume an `items`,
 * `results`, `data`, or other backend property.
 */
export function toEvidenceItems(
  source: unknown
): EvidenceItem[] {
  if (!Array.isArray(source)) {
    return [];
  }

  return source
    .map(toEvidenceItem)
    .filter(
      (
        item
      ): item is EvidenceItem =>
        item !== null
    );
}

export function toDecisionPanelData(
  source: unknown
): DecisionPanelData {
  if (!isRecord(source)) {
    return {};
  }

  return copyExistingFields<DecisionPanelData>(
    source,
    decisionKeys
  ) as DecisionPanelData;
}

export function toRiskPanelData(
  source: unknown
): RiskPanelData {
  if (!isRecord(source)) {
    return {};
  }

  return copyExistingFields<RiskPanelData>(
    source,
    riskKeys
  ) as RiskPanelData;
}
