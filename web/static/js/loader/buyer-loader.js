import { buyer } from "../api-client";
import { createPageLoader } from "../page-loader";

export interface BuyerPageData {
  markets: Awaited<ReturnType<typeof buyer.markets>>;
  strategies: Awaited<ReturnType<typeof buyer.strategies>>;
  pipeline: Awaited<ReturnType<typeof buyer.pipeline>>;
  decision: Awaited<ReturnType<typeof buyer.decision>>;
  risk: Awaited<ReturnType<typeof buyer.risk>>;
  cas: Awaited<ReturnType<typeof buyer.cas>>;
  casGates: Awaited<ReturnType<typeof buyer.casGates>>;
  plus: Awaited<ReturnType<typeof buyer.plus>>;
  health: Awaited<ReturnType<typeof buyer.health>>;
}

export async function fetchBuyerPage(): Promise<BuyerPageData> {
  const [
    markets,
    strategies,
    pipeline,
    decision,
    risk,
    cas,
    casGates,
    plus,
    health
  ] = await Promise.all([
    buyer.markets(),
    buyer.strategies(),
    buyer.pipeline(),
    buyer.decision(),
    buyer.risk(),
    buyer.cas(),
    buyer.casGates(),
    buyer.plus(),
    buyer.health()
  ]);

  return {
    markets,
    strategies,
    pipeline,
    decision,
    risk,
    cas,
    casGates,
    plus,
    health
  };
}

export function createBuyerLoader() {
  return createPageLoader<BuyerPageData>(
    fetchBuyerPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}