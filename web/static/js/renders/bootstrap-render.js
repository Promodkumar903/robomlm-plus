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

import { renderTerminal } from "./renderers/terminal-renderer";
import { renderDiscovery } from "./renderers/discovery-renderer";
import { renderBuyer } from "./renderers/buyer-renderer";
import { renderMemory } from "./renderers/memory-renderer";
import { renderResearch } from "./renderers/research-renderer";
import { renderAutomation } from "./renderers/automation-renderer";
import { renderAccount } from "./renderers/account-renderer";

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