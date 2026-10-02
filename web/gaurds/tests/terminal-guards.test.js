import { describe, expect, it } from "vitest";

import {
  isTerminalPageData,
  isEvidenceItem,
  isDecisionPanelData,
  isRiskPanelData
} from "../index";

function validTerminalPageData(): unknown {
  return {
    overview: {},
    context: {},
    evidence: [
      {
        id: "EV-001",
        source: "test-source",
        title: "Test evidence",
        claim: "Test claim",
        timestamp: "2026-09-16T00:00:00Z",
        confidence: 0.91,
        status: "verified"
      }
    ],
    intelligence: {},
    decision: {
      decision: "HOLD",
      action: "NO_ACTION",
      rationale: "Test rationale",
      confidence: 0.88,
      timestamp: "2026-09-16T00:00:00Z",
      evidenceIds: ["EV-001"]
    },
    risk: {
      level: "LOW",
      status: "CLEAR",
      summary: "Test risk summary",
      exposure: 1000,
      maxLoss: 100,
      warnings: [],
      gates: []
    },
    layers: {},
    pipeline: {},
    portfolio: {},
    positions: [],
    backendHealth: {
      ok: true
    }
  };
}

describe("Terminal runtime guards", () => {
  describe("isTerminalPageData", () => {
    it("accepts a valid TerminalPageData payload", () => {
      const payload = validTerminalPageData();

      expect(isTerminalPageData(payload)).toBe(true);
    });

    it("accepts unknown backend fields without rejecting the payload", () => {
      const payload = validTerminalPageData();

      if (
        typeof payload !== "object" ||
        payload === null
      ) {
        throw new Error("Test fixture is invalid");
      }

      const record = payload as Record<string, unknown>;

      record.backendTraceId = "trace-123";
      record.futureBackendField = {
        version: 2,
        internal: true
      };

      expect(
        isTerminalPageData(record)
      ).toBe(true);

      expect(
        record.backendTraceId
      ).toBe("trace-123");

      expect(
        record.futureBackendField
      ).toEqual({
        version: 2,
        internal: true
      });
    });
  });

  describe("evidence guard", () => {
    it("accepts valid evidence", () => {
      expect(
        isEvidenceItem({
          id: "EV-001",
          source: "source-a",
          title: "Evidence",
          claim: "Claim",
          timestamp: "2026-09-16T00:00:00Z",
          confidence: 0.9,
          status: "verified"
        })
      ).toBe(true);
    });

    it("rejects malformed evidence confidence", () => {
      expect(
        isEvidenceItem({
          id: "EV-001",
          source: "source-a",
          title: "Evidence",
          claim: "Claim",
          timestamp: "2026-09-16T00:00:00Z",
          confidence: "high",
          status: "verified"
        })
      ).toBe(false);
    });

    it("rejects malformed evidence timestamp", () => {
      expect(
        isEvidenceItem({
          id: "EV-001",
          source: "source-a",
          title: "Evidence",
          claim: "Claim",
          timestamp: 123456,
          confidence: 0.9,
          status: "verified"
        })
      ).toBe(false);
    });

    it("preserves unknown evidence fields while accepting them", () => {
      const evidence = {
        id: "EV-001",
        source: "source-a",
        title: "Evidence",
        claim: "Claim",
        timestamp: "2026-09-16T00:00:00Z",
        confidence: 0.9,
        status: "verified",

        backendEvidenceHash: "abc123",
        backendOnlyMetadata: {
          engine: "D6",
          revision: 4
        }
      };

      expect(
        isEvidenceItem(evidence)
      ).toBe(true);

      expect(
        evidence.backendEvidenceHash
      ).toBe("abc123");

      expect(
        evidence.backendOnlyMetadata
      ).toEqual({
        engine: "D6",
        revision: 4
      });
    });
  });

  describe("decision guard", () => {
    it("accepts valid decision payload", () => {
      expect(
        isDecisionPanelData({
          decision: "HOLD",
          action: "NO_ACTION",
          rationale: "Test rationale",
          confidence: 0.87,
          timestamp: "2026-09-16T00:00:00Z",
          evidenceIds: ["EV-001"]
        })
      ).toBe(true);
    });

    it("rejects malformed decision confidence", () => {
      expect(
        isDecisionPanelData({
          decision: "HOLD",
          action: "NO_ACTION",
          rationale: "Test rationale",
          confidence: "0.87",
          timestamp: "2026-09-16T00:00:00Z",
          evidenceIds: ["EV-001"]
        })
      ).toBe(false);
    });

    it("rejects malformed decision evidenceIds", () => {
      expect(
        isDecisionPanelData({
          decision: "HOLD",
          action: "NO_ACTION",
          rationale: "Test rationale",
          confidence: 0.87,
          timestamp: "2026-09-16T00:00:00Z",
          evidenceIds: [123]
        })
      ).toBe(false);
    });

    it("preserves unknown decision fields while accepting them", () => {
      const decision = {
        decision: "HOLD",
        action: "NO_ACTION",
        rationale: "Test rationale",
        confidence: 0.87,
        timestamp: "2026-09-16T00:00:00Z",
        evidenceIds: ["EV-001"],

        backendDecisionId: "DEC-123",
        decisionEngineVersion: "D6-v1"
      };

      expect(
        isDecisionPanelData(decision)
      ).toBe(true);

      expect(
        decision.backendDecisionId
      ).toBe("DEC-123");

      expect(
        decision.decisionEngineVersion
      ).toBe("D6-v1");
    });
  });

  describe("risk guard", () => {
    it("accepts valid risk payload", () => {
      expect(
        isRiskPanelData({
          level: "LOW",
          status: "CLEAR",
          summary: "Test risk",
          exposure: 1000,
          maxLoss: 100,
          warnings: [],
          gates: []
        })
      ).toBe(true);
    });

    it("rejects malformed risk exposure", () => {
      expect(
        isRiskPanelData({
          level: "LOW",
          status: "CLEAR",
          summary: "Test risk",
          exposure: "1000",
          maxLoss: 100,
          warnings: [],
          gates: []
        })
      ).toBe(false);
    });

    it("rejects malformed risk warnings", () => {
      expect(
        isRiskPanelData({
          level: "LOW",
          status: "CLEAR",
          summary: "Test risk",
          exposure: 1000,
          maxLoss: 100,
          warnings: ["valid", 123],
          gates: []
        })
      ).toBe(false);
    });

    it("rejects malformed risk gates when gates is not an array", () => {
      expect(
        isRiskPanelData({
          level: "LOW",
          status: "CLEAR",
          summary: "Test risk",
          exposure: 1000,
          maxLoss: 100,
          warnings: [],
          gates: {}
        })
      ).toBe(false);
    });

    it("preserves unknown risk fields while accepting them", () => {
      const risk = {
        level: "LOW",
        status: "CLEAR",
        summary: "Test risk",
        exposure: 1000,
        maxLoss: 100,
        warnings: [],
        gates: [],

        backendRiskId: "RISK-123",
        riskEngineVersion: "RISK-v4",
        backendOnlyDiagnostics: {
          calculation: "internal"
        }
      };

      expect(
        isRiskPanelData(risk)
      ).toBe(true);

      expect(
        risk.backendRiskId
      ).toBe("RISK-123");

      expect(
        risk.riskEngineVersion
      ).toBe("RISK-v4");

      expect(
        risk.backendOnlyDiagnostics
      ).toEqual({
        calculation: "internal"
      });
    });
  });

  describe("nested malformed payloads", () => {
    it("rejects malformed nested evidence inside TerminalPageData", () => {
      const payload =
        validTerminalPageData() as Record<string, unknown>;

      payload.evidence = [
        {
          id: "EV-001",
          source: "source-a",
          title: "Evidence",
          claim: "Claim",
          timestamp: "2026-09-16T00:00:00Z",
          confidence: "invalid",
          status: "verified"
        }
      ];

      expect(
        isTerminalPageData(payload)
      ).toBe(false);
    });

    it("rejects malformed nested decision inside TerminalPageData", () => {
      const payload =
        validTerminalPageData() as Record<string, unknown>;

      payload.decision = {
        decision: "HOLD",
        action: "NO_ACTION",
        rationale: "Test",
        confidence: "invalid",
        timestamp: "2026-09-16T00:00:00Z",
        evidenceIds: ["EV-001"]
      };

      expect(
        isTerminalPageData(payload)
      ).toBe(false);
    });

    it("rejects malformed nested risk inside TerminalPageData", () => {
      const payload =
        validTerminalPageData() as Record<string, unknown>;

      payload.risk = {
        level: "LOW",
        status: "CLEAR",
        summary: "Test",
        exposure: "invalid",
        maxLoss: 100,
        warnings: [],
        gates: []
      };

      expect(
        isTerminalPageData(payload)
      ).toBe(false);
    });
  });
});