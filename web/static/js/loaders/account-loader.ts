import { account } from "../api-client";
import { createPageLoader } from "../page-loader";

export interface AccountPageData {
  summary: Awaited<ReturnType<typeof account.summary>>;
  equity: Awaited<ReturnType<typeof account.equity>>;
  allocation: Awaited<ReturnType<typeof account.allocation>>;
  status: Awaited<ReturnType<typeof account.status>>;
  backendMap: Awaited<ReturnType<typeof account.backendMap>>;
}

export async function fetchAccountPage(): Promise<AccountPageData> {
  const [
    summary,
    equity,
    allocation,
    status,
    backendMap
  ] = await Promise.all([
    account.summary(),
    account.equity(),
    account.allocation(),
    account.status(),
    account.backendMap()
  ]);

  return {
    summary,
    equity,
    allocation,
    status,
    backendMap
  };
}

export function createAccountLoader() {
  return createPageLoader<AccountPageData>(
    fetchAccountPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}