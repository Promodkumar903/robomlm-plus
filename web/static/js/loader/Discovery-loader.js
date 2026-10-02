import { discovery } from "./api-client";

export async function loadDiscovery() {
  return Promise.all([
    discovery.overview(),
    discovery.engines(),
    discovery.scanner(),
    discovery.opportunities(),
    discovery.top10(),
    discovery.gates(),
    discovery.provenance(),
    discovery.health()
  ]);
}