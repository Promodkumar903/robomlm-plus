import { discovery } from "../api-client";

export interface DiscoveryPageData {
  overview: unknown;
  engines: unknown;
  scanner: unknown;
  opportunities: unknown;
  top10: unknown;
  gates: unknown;
  provenance: unknown;
  health: unknown;
}

export function createDiscoveryLoader() {
  return {
    async load() {
      const [
        overview,
        engines,
        scanner,
        opportunities,
        top10,
        gates,
        provenance,
        health
      ] = await Promise.all([
        discovery.overview(),
        discovery.engines(),
        discovery.scanner(),
        discovery.opportunities(),
        discovery.top10(),
        discovery.gates(),
        discovery.provenance(),
        discovery.health()
      ]);

      return {
        status: "ready" as const,
        error: null,
        data: {
          overview,
          engines,
          scanner,
          opportunities,
          top10,
          gates,
          provenance,
          health
        }
      };
    },

    getState() {
      return {
        status: "ready" as const,
        error: null,
        data: null
      };
    }
  };
}