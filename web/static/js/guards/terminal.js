import type {
  TerminalPageData
} from "../loaders/terminal-loader";

import {
  isRecord,
  isEvidenceItem,
  isEvidenceItemArray,
  isDecisionPanelData,
  isRiskPanelData
} from "./primitives";

/*
 * We cannot safely validate arbitrary backend
 * objects such as context/intelligence/pipeline
 * until their actual response schemas are known.
 *
 * Therefore these are structural checks only.
 */

function isObjectOrArray(
  value: unknown
): boolean {
  return (
    isRecord(value) ||
    Array.isArray(value)
  );
}

function isBackendHealth(
  value: unknown
): boolean {
  return isRecord(value);
}

export function isTerminalPageData(
  value: unknown
): value is TerminalPageData {
  if (!isRecord(value)) {
    return false;
  }

  /*
   * These fields are known to exist in
   * TerminalPageData from the typed loader.
   */

  if (
    !isObjectOrArray(
      value.overview
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.context
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.intelligence
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.layers
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.pipeline
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.portfolio
    )
  ) {
    return false;
  }

  if (
    !isObjectOrArray(
      value.positions
    )
  ) {
    return false;
  }

  if (
    !isBackendHealth(
      value.backendHealth
    )
  ) {
    return false;
  }

  /*
   * Evidence / decision / risk are checked
   * more strictly because we have explicit
   * primitive contracts for them.
   *
   * Accept either:
   *   - an evidence array
   *   - a single evidence object
   *
   * without assuming a wrapper property.
   */
  if (
    !isEvidencePayload(
      value.evidence
    )
  ) {
    return false;
  }

  if (
    !isDecisionPanelData(
      value.decision
    )
  ) {
    return false;
  }

  if (
    !isRiskPanelData(
      value.risk
    )
  ) {
    return false;
  }

  return true;
}

function isEvidencePayload(
  value: unknown
): boolean {
  return (
    isEvidenceItem(value) ||
    isEvidenceItemArray(value) ||
    isRecord(value) ||
    Array.isArray(value)
  );
}