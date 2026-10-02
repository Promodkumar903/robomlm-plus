import { memory } from "../api-client";
import { createPageLoader } from "../page-loader";

export interface MemoryPageData {
  overview: Awaited<ReturnType<typeof memory.overview>>;
  decision: Awaited<ReturnType<typeof memory.decision>>;
  evidence: Awaited<ReturnType<typeof memory.evidence>>;
  outcome: Awaited<ReturnType<typeof memory.outcome>>;
  pattern: Awaited<ReturnType<typeof memory.pattern>>;
}

export async function fetchMemoryPage(): Promise<MemoryPageData> {
  const [
    overview,
    decision,
    evidence,
    outcome,
    pattern
  ] = await Promise.all([
    memory.overview(),
    memory.decision(),
    memory.evidence(),
    memory.outcome(),
    memory.pattern()
  ]);

  return {
    overview,
    decision,
    evidence,
    outcome,
    pattern
  };
}

export function createMemoryLoader() {
  return createPageLoader<MemoryPageData>(
    fetchMemoryPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}