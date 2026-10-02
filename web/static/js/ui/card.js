import type {
  CardOptions
} from "./types";

import {
  el,
  text
} from "./dom";

export function createCard(
  options: CardOptions
): HTMLElement {
  const card = el("section", "ui-card");

  if (options.className) {
    card.classList.add(
      options.className
    );
  }

  if (options.tone) {
    card.dataset.tone =
      options.tone;
  }

  const header = el(
    "header",
    "ui-card__header"
  );

  const title = el(
    "h3",
    "ui-card__title"
  );

  title.appendChild(
    text(options.title)
  );

  header.appendChild(title);

  if (options.subtitle) {
    const subtitle = el(
      "p",
      "ui-card__subtitle"
    );

    subtitle.appendChild(
      text(options.subtitle)
    );

    header.appendChild(
      subtitle
    );
  }

  card.appendChild(header);

  return card;
}

export function cardBody(
  card: HTMLElement
): HTMLElement {
  const body = el(
    "div",
    "ui-card__body"
  );

  card.appendChild(body);

  return body;
}