import type {
  EvidenceItem
} from "./types";

import {
  el,
  text
} from "./dom";

import {
  createStatusBadge,
  statusTone
} from "./status-badge";

export function createEvidencePanel(
  items: EvidenceItem[]
): HTMLElement {
  const panel = el(
    "section",
    "ui-evidence-panel"
  );

  const title = el(
    "h3",
    "ui-panel-title"
  );

  title.textContent =
    "Evidence";

  panel.appendChild(title);

  if (items.length === 0) {
    const empty = el(
      "div",
      "ui-empty"
    );

    empty.textContent =
      "No evidence available.";

    panel.appendChild(empty);

    return panel;
  }

  const list = el(
    "div",
    "ui-evidence-list"
  );

  for (const item of items) {
    const evidence = el(
      "article",
      "ui-evidence-item"
    );

    if (item.title) {
      const heading = el("h4");
      heading.textContent =
        item.title;
      evidence.appendChild(
        heading
      );
    }

    if (item.source) {
      const source = el(
        "div",
        "ui-evidence-source"
      );

      source.textContent =
        item.source;

      evidence.appendChild(
        source
      );
    }

    if (item.claim) {
      const claim = el(
        "p",
        "ui-evidence-claim"
      );

      claim.textContent =
        item.claim;

      evidence.appendChild(
        claim
      );
    }

    if (item.status) {
      evidence.appendChild(
        createStatusBadge(
          item.status,
          statusTone(
            item.status
          )
        )
      );
    }

    if (
      item.timestamp
    ) {
      const timestamp =
        el(
          "time",
          "ui-evidence-time"
        );

      timestamp.textContent =
        item.timestamp;

      evidence.appendChild(
        timestamp
      );
    }

    list.appendChild(
      evidence
    );
  }

  panel.appendChild(list);

  return panel;
}