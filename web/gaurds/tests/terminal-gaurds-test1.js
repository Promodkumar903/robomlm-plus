describe("supported evidence wrapper shapes", () => {
  it("accepts evidence as a direct EvidenceItem array", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = [
      {
        id: "EV-001",
        source: "source-a",
        title: "Evidence",
        claim: "Claim",
        timestamp: "2026-09-16T00:00:00Z",
        confidence: 0.91,
        status: "verified"
      },
      {
        id: "EV-002",
        source: "source-b",
        title: "Second evidence",
        claim: "Second claim",
        timestamp: "2026-09-16T00:01:00Z",
        confidence: null,
        status: "pending"
      }
    ];

    expect(
      isTerminalPageData(payload)
    ).toBe(true);
  });

  it("accepts an opaque backend evidence object", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = {
      backendPayload: {
        engine: "evidence-engine",
        revision: 7
      },
      opaqueTrace: "trace-001",
      futureField: {
        nested: true
      }
    };

    expect(
      isTerminalPageData(payload)
    ).toBe(true);
  });

  it("does not require an items field on an opaque evidence object", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = {
      backendEvidenceEnvelope: true,
      providerPayload: {
        arbitrary: "backend-defined"
      }
    };

    expect(
      isTerminalPageData(payload)
    ).toBe(true);
  });

  it("accepts an empty opaque evidence object", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = {};

    expect(
      isTerminalPageData(payload)
    ).toBe(true);
  });

  it("does not interpret unknown wrapper fields", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = {
      items: "not-an-array",
      data: 123,
      results: null,
      backendSpecificValue: {
        value: "opaque"
      }
    };

    /*
     * This remains valid because the object is treated
     * as opaque. We deliberately do not claim that
     * `items`, `data`, or `results` have any meaning.
     */
    expect(
      isTerminalPageData(payload)
    ).toBe(true);
  });

  it("rejects an evidence array containing a malformed item", () => {
    const payload =
      validTerminalPageData() as Record<string, unknown>;

    payload.evidence = [
      {
        id: "EV-001",
        source: "source-a",
        title: "Valid evidence",
        claim: "Valid claim",
        timestamp: "2026-09-16T00:00:00Z",
        confidence: 0.91,
        status: "verified"
      },
      {
        id: "EV-002",
        source: "source-b",
        title: "Malformed evidence",
        claim: "Invalid confidence",
        timestamp: "2026-09-16T00:01:00Z",
        confidence: "not-a-number",
        status: "verified"
      }
    ];

    expect(
      isTerminalPageData(payload)
    ).toBe(false);
  });
});