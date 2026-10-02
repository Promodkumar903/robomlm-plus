import { automation } from "../api-client";
import { createPageLoader } from "../page-loader";

export interface AutomationPageData {
  overview: Awaited<ReturnType<typeof automation.overview>>;
  mode: Awaited<ReturnType<typeof automation.mode>>;
  execution: Awaited<ReturnType<typeof automation.execution>>;
  killSwitch: Awaited<ReturnType<typeof automation.killSwitch>>;
  reconciliation: Awaited<ReturnType<typeof automation.reconciliation>>;
}

export async function fetchAutomationPage(): Promise<AutomationPageData> {
  const [
    overview,
    mode,
    execution,
    killSwitch,
    reconciliation
  ] = await Promise.all([
    automation.overview(),
    automation.mode(),
    automation.execution(),
    automation.killSwitch(),
    automation.reconciliation()
  ]);

  return {
    overview,
    mode,
    execution,
    killSwitch,
    reconciliation
  };
}

export function createAutomationLoader() {
  return createPageLoader<AutomationPageData>(
    fetchAutomationPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}