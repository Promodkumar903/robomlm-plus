import type {
  DecisionPanelData
} from "./types";

import {
  el
} from "./dom";

import {
  createStatusBadge,
  statusTone
} from "./status-badge";

export function createDecisionPanel(
  data: DecisionPanelData
): HTMLElement {
  const panel = el(
    "section",
    "ui-decision-panel"
  );

  const title = el(
    "h3",
    "ui-panel-title"
  );

  title.textContent =
    "Decision";

  panel.appendChild(title);

  if (data.decision) {
    const decision =
      el(
        "div",
        "ui-decision-value"
      );

    decision.textContent =
      data.decision;

    panel.appendChild(
      decision
    );
  }

  if (data.action) {
    panel.appendChild(
      createStatusBadge(
        data.action,
        statusTone(
          data.action
        )
      )
    );
  }

  if (data.rationale) {
    const rationale =
      el(
        "p",
        "ui-decision-rationale"
      );

    rationale.textContent =
      data.rationale;

    panel.appendChild(
      rationale
    );
  }

  if (
    data.confidence != null
  ) {
    const confidence =
      el(
        "div",
        "ui-decision-confidence"
      );

    confidence.textContent =
      `Confidence: ${data.confidence}`;

    panel.appendChild(
      confidence
    );
  }

  if (data.timestamp) {
    const time = el("time");

    time.textContent =
      data.timestamp;

    panel.appendChild(time);
  }

  return panel;
}