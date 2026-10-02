import type {
  RiskPanelData
} from "./types";

import {
  el
} from "./dom";

import {
  createStatusBadge,
  statusTone
} from "./status-badge";

export function createRiskPanel(
  data: RiskPanelData
): HTMLElement {
  const panel = el(
    "section",
    "ui-risk-panel"
  );

  const title = el(
    "h3",
    "ui-panel-title"
  );

  title.textContent =
    "Risk";

  panel.appendChild(title);

  if (data.level) {
    panel.appendChild(
      createStatusBadge(
        data.level,
        statusTone(
          data.level
        )
      )
    );
  }

  if (data.status) {
    panel.appendChild(
      createStatusBadge(
        data.status,
        statusTone(
          data.status
        )
      )
    );
  }

  if (data.summary) {
    const summary =
      el(
        "p",
        "ui-risk-summary"
      );

    summary.textContent =
      data.summary;

    panel.appendChild(
      summary
    );
  }

  if (
    data.exposure != null
  ) {
    const exposure =
      el(
        "div",
        "ui-risk-metric"
      );

    exposure.textContent =
      `Exposure: ${data.exposure}`;

    panel.appendChild(
      exposure
    );
  }

  if (
    data.maxLoss != null
  ) {
    const loss =
      el(
        "div",
        "ui-risk-metric"
      );

    loss.textContent =
      `Max loss: ${data.maxLoss}`;

    panel.appendChild(loss);
  }

  if (
    data.warnings &&
    data.warnings.length > 0
  ) {
    const list =
      el(
        "ul",
        "ui-risk-warnings"
      );

    for (
      const warning
      of data.warnings
    ) {
      const item =
        el("li");

      item.textContent =
        warning;

      list.appendChild(item);
    }

    panel.appendChild(list);
  }

  return panel;
}