import { research } from "../api-client";
import { createPageLoader } from "../page-loader";

export interface ResearchPageData {
  overview: Awaited<ReturnType<typeof research.overview>>;
  hypothesis: Awaited<ReturnType<typeof research.hypothesis>>;
  experiment: Awaited<ReturnType<typeof research.experiment>>;
  validation: Awaited<ReturnType<typeof research.validation>>;
  stress: Awaited<ReturnType<typeof research.stress>>;
  candidate: Awaited<ReturnType<typeof research.candidate>>;
  version: Awaited<ReturnType<typeof research.version>>;
  deployment: Awaited<ReturnType<typeof research.deployment>>;
}

export async function fetchResearchPage(): Promise<ResearchPageData> {
  const [
    overview,
    hypothesis,
    experiment,
    validation,
    stress,
    candidate,
    version,
    deployment
  ] = await Promise.all([
    research.overview(),
    research.hypothesis(),
    research.experiment(),
    research.validation(),
    research.stress(),
    research.candidate(),
    research.version(),
    research.deployment()
  ]);

  return {
    overview,
    hypothesis,
    experiment,
    validation,
    stress,
    candidate,
    version,
    deployment
  };
}

export function createResearchLoader() {
  return createPageLoader<ResearchPageData>(
    fetchResearchPage,
    {
      loading: document.querySelector("#page-loading"),
      content: document.querySelector("#page-content"),
      error: document.querySelector("#page-error")
    }
  );
}