import type { TerminalPageData } from "../loaders/terminal-loader";
import {
  text,
  json
} from "../page-renderer";

export function renderTerminal(
  data: TerminalPageData
): void {
  json(
    "terminal-overview",
    data.overview
  );

  json(
    "terminal-context",
    data.context
  );

  json(
    "terminal-evidence",
    data.evidence
  );

  json(
    "terminal-intelligence",
    data.intelligence
  );

  json(
    "terminal-decision",
    data.decision
  );

  json(
    "terminal-risk",
    data.risk
  );

  json(
    "terminal-cas",
    data.cas
  );

  json(
    "terminal-pipeline",
    data.pipeline
  );

  json(
    "terminal-portfolio",
    data.portfolio
  );

  json(
    "terminal-positions",
    data.positions
  );

  const backendHealth =
  data.backendHealth as {
    status?: string;
  };

text(
  "terminal-status",
  backendHealth?.status ?? "unknown"
);
}
