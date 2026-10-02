import {
  terminal,
  backend
} from "../api-client";

import {
  createPageLoader
} from "../page-loader";

export interface TerminalPageData {
  overview: Awaited<ReturnType<typeof terminal.overview>>;
  context: Awaited<ReturnType<typeof terminal.context>>;
  evidence: Awaited<ReturnType<typeof terminal.evidence>>;
  intelligence: Awaited<ReturnType<typeof terminal.intelligence>>;
  decision: Awaited<ReturnType<typeof terminal.decision>>;
  risk: Awaited<ReturnType<typeof terminal.risk>>;
  cas: Awaited<ReturnType<typeof terminal.cas>>;
  layers: Awaited<ReturnType<typeof terminal.layers>>;
  pipeline: Awaited<ReturnType<typeof terminal.pipeline>>;
  portfolio: Awaited<ReturnType<typeof terminal.portfolio>>;
  positions: Awaited<ReturnType<typeof terminal.positions>>;
  backendHealth: Awaited<ReturnType<typeof backend.health>>;
}

export async function fetchTerminalPage(): Promise<TerminalPageData> {
  const [
    overview,
    context,
    evidence,
    intelligence,
    decision,
    risk,
    cas,
    layers,
    pipeline,
    portfolio,
    positions,
    backendHealth
  ] = await Promise.all([
    terminal.overview(),
    terminal.context(),
    terminal.evidence(),
    terminal.intelligence(),
    terminal.decision(),
    terminal.risk(),
    terminal.cas(),
    terminal.layers(),
    terminal.pipeline(),
    terminal.portfolio(),
    terminal.positions(),
    backend.health()
  ]);

  return {
    overview,
    context,
    evidence,
    intelligence,
    decision,
    risk,
    cas,
    layers,
    pipeline,
    portfolio,
    positions,
    backendHealth
  };
}

export function createTerminalLoader() {
  return createPageLoader<TerminalPageData>(
    fetchTerminalPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}