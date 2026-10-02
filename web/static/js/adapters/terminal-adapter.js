import type {
  TerminalPageData
} from "../loaders/terminal-loader";

import type {
  EvidenceItem,
  DecisionPanelData,
  RiskPanelData
} from "../ui";

import {
  toEvidenceItems,
  toDecisionPanelData,
  toRiskPanelData
} from "./primitive-adapters";

import {
  isTerminalPageData
} from "../guards";

export interface TerminalUIData {
  terminal: TerminalPageData;
  evidence: EvidenceItem[];
  decision: DecisionPanelData;
  risk: RiskPanelData;
}

export function toTerminalUIData(
  data: TerminalPageData
): TerminalUIData {
  if (!isTerminalPageData(data)) {
    throw new Error(
      "Invalid TerminalPageData received from backend."
    );
  }

  return {
    terminal: data,

    evidence:
      toEvidenceItems(
        data.evidence
      ),

    decision:
      toDecisionPanelData(
        data.decision
      ),

    risk:
      toRiskPanelData(
        data.risk
      )
  };
}