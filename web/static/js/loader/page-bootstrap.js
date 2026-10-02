import {
  createTerminalLoader,
  type TerminalPageData
} from "./loaders/terminal-loader";

import {
  createDiscoveryLoader,
  type DiscoveryPageData
} from "./loaders/discovery-loader";

import {
  createBuyerLoader,
  type BuyerPageData
} from "./loaders/buyer-loader";

import {
  createMemoryLoader,
  type MemoryPageData
} from "./loaders/memory-loader";

import {
  createResearchLoader,
  type ResearchPageData
} from "./loaders/research-loader";

import {
  createAutomationLoader,
  type AutomationPageData
} from "./loaders/automation-loader";

import {
  createAccountLoader,
  type AccountPageData
} from "./loaders/account-loader";

import type { PageLoader } from "./page-loader";

interface PageDefinition<T> {
  createLoader: () => PageLoader<T>;
  render: (data: T) => void | Promise<void>;
}

type PageRegistry = {
  "/terminal": PageDefinition<TerminalPageData>;
  "/discovery": PageDefinition<DiscoveryPageData>;
  "/buyer": PageDefinition<BuyerPageData>;
  "/memory": PageDefinition<MemoryPageData>;
  "/research": PageDefinition<ResearchPageData>;
  "/automation": PageDefinition<AutomationPageData>;
  "/account": PageDefinition<AccountPageData>;
};

const pageRegistry: PageRegistry = {
  "/terminal": {
    createLoader: createTerminalLoader,
    render: renderTerminal
  },

  "/discovery": {
    createLoader: createDiscoveryLoader,
    render: renderDiscovery
  },

  "/buyer": {
    createLoader: createBuyerLoader,
    render: renderBuyer
  },

  "/memory": {
    createLoader: createMemoryLoader,
    render: renderMemory
  },

  "/research": {
    createLoader: createResearchLoader,
    render: renderResearch
  },

  "/automation": {
    createLoader: createAutomationLoader,
    render: renderAutomation
  },

  "/account": {
    createLoader: createAccountLoader,
    render: renderAccount
  }
};

type PagePath = keyof PageRegistry;

function normalizePath(pathname: string): string {
  const normalized = pathname.replace(/\/+$/, "");
  return normalized || "/";
}

function isPagePath(path: string): path is PagePath {
  return path in pageRegistry;
}

export function getCurrentPage(): PagePath | null {
  const path = normalizePath(window.location.pathname);

  return isPagePath(path)
    ? path
    : null;
}

export async function bootstrapPage(): Promise<void> {
  const path = getCurrentPage();

  if (!path) {
    return;
  }

  await bootstrapRegisteredPage(
    pageRegistry[path]
  );
}

async function bootstrapRegisteredPage<T>(
  definition: PageDefinition<T>
): Promise<void> {
  const loader = definition.createLoader();

  const state = await loader.load();

  if (state.status !== "ready") {
    return;
  }

  if (state.data === null) {
    return;
  }

  await definition.render(state.data);
}

/* ---------- Renderers ---------- */

function renderTerminal(
  data: TerminalPageData
): void {
  setJson("terminal-overview", data.overview);
  setJson("terminal-context", data.context);
  setJson("terminal-evidence", data.evidence);
  setJson("terminal-intelligence", data.intelligence);
  setJson("terminal-decision", data.decision);
  setJson("terminal-risk", data.risk);
  setJson("terminal-cas", data.cas);
  setJson("terminal-layers", data.layers);
  setJson("terminal-pipeline", data.pipeline);
  setJson("terminal-portfolio", data.portfolio);
  setJson("terminal-positions", data.positions);
}

function renderDiscovery(
  data: DiscoveryPageData
): void {
  setJson("discovery-overview", data.overview);
  setJson("discovery-engines", data.engines);
  setJson("discovery-scanner", data.scanner);
  setJson("discovery-opportunities", data.opportunities);
  setJson("discovery-top10", data.top10);
  setJson("discovery-gates", data.gates);
  setJson("discovery-provenance", data.provenance);
}

function renderBuyer(
  data: BuyerPageData
): void {
  setJson("buyer-markets", data.markets);
  setJson("buyer-strategies", data.strategies);
  setJson("buyer-pipeline", data.pipeline);
  setJson("buyer-decision", data.decision);
  setJson("buyer-risk", data.risk);
  setJson("buyer-cas", data.cas);
  setJson("buyer-cas-gates", data.casGates);
  setJson("buyer-plus", data.plus);
}

function renderMemory(
  data: MemoryPageData
): void {
  setJson("memory-overview", data.overview);
  setJson("memory-decision", data.decision);
  setJson("memory-evidence", data.evidence);
  setJson("memory-outcome", data.outcome);
  setJson("memory-pattern", data.pattern);
}

function renderResearch(
  data: ResearchPageData
): void {
  setJson("research-overview", data.overview);
  setJson("research-hypothesis", data.hypothesis);
  setJson("research-experiment", data.experiment);
  setJson("research-validation", data.validation);
  setJson("research-stress", data.stress);
  setJson("research-candidate", data.candidate);
  setJson("research-version", data.version);
  setJson("research-deployment", data.deployment);
}

function renderAutomation(
  data: AutomationPageData
): void {
  setJson("automation-overview", data.overview);
  setJson("automation-mode", data.mode);
  setJson("automation-execution", data.execution);
  setJson("automation-kill-switch", data.killSwitch);
  setJson(
    "automation-reconciliation",
    data.reconciliation
  );
}

function renderAccount(
  data: AccountPageData
): void {
  setJson("account-summary", data.summary);
  setJson("account-equity", data.equity);
  setJson("account-allocation", data.allocation);
  setJson("account-status", data.status);
  setJson(
    "account-backend-map",
    data.backendMap
  );
}

function setJson(
  elementId: string,
  value: unknown
): void {
  const element = document.getElementById(elementId);

  if (!element) {
    return;
  }

  element.textContent = JSON.stringify(
    value,
    null,
    2
  );
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    () => void bootstrapPage()
  );
} else {
  void bootstrapPage();
}