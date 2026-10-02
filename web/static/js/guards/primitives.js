import type {
  EvidenceItem,
  DecisionPanelData,
  RiskPanelData
} from "../ui";

export function isRecord(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function isStringOrUndefined(
  value: unknown
): value is string | undefined {
  return (
    value === undefined ||
    typeof value === "string"
  );
}

function isNumberOrNullOrUndefined(
  value: unknown
): value is number | null | undefined {
  return (
    value === undefined ||
    value === null ||
    typeof value === "number"
  );
}

function isStringArrayOrUndefined(
  value: unknown
): value is string[] | undefined {
  return (
    value === undefined ||
    (
      Array.isArray(value) &&
      value.every(
        item => typeof item === "string"
      )
    )
  );
}

export function isEvidenceItem(
  value: unknown
): value is EvidenceItem {
  if (!isRecord(value)) {
    return false;
  }

  /*
   * Only validate fields that are part of our
   * existing UI contract.
   *
   * Unknown backend fields are ignored.
   */
  if (
    !isStringOrUndefined(value.id)
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(value.source)
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(value.title)
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(value.claim)
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(value.timestamp)
  ) {
    return false;
  }

  if (
    !isNumberOrNullOrUndefined(
      value.confidence
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(value.status)
  ) {
    return false;
  }

  return true;
}

export function isEvidenceItemArray(
  value: unknown
): value is EvidenceItem[] {
  return (
    Array.isArray(value) &&
    value.every(isEvidenceItem)
  );
}

export function isDecisionPanelData(
  value: unknown
): value is DecisionPanelData {
  if (!isRecord(value)) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.decision
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.action
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.rationale
    )
  ) {
    return false;
  }

  if (
    !isNumberOrNullOrUndefined(
      value.confidence
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.timestamp
    )
  ) {
    return false;
  }

  if (
    !isStringArrayOrUndefined(
      value.evidenceIds
    )
  ) {
    return false;
  }

  return true;
}

export function isRiskPanelData(
  value: unknown
): value is RiskPanelData {
  if (!isRecord(value)) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.level
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.status
    )
  ) {
    return false;
  }

  if (
    !isStringOrUndefined(
      value.summary
    )
  ) {
    return false;
  }

  if (
    !isNumberOrNullOrUndefined(
      value.exposure
    )
  ) {
    return false;
  }

  if (
    !isNumberOrNullOrUndefined(
      value.maxLoss
    )
  ) {
    return false;
  }

  if (
    value.warnings !== undefined &&
    (
      !Array.isArray(value.warnings) ||
      !value.warnings.every(
        item =>
          typeof item === "string"
      )
    )
  ) {
    return false;
  }

  /*
   * `gates` is intentionally only checked as
   * an array because the backend gate schema has
   * not been established here.
   */
  if (
    value.gates !== undefined &&
    !Array.isArray(value.gates)
  ) {
    return false;
  }

  return true;
}