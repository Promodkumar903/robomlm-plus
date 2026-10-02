import {
  el
} from "./dom";

export function createEmptyState(
  message = "No data available."
): HTMLElement {
  const element = el(
    "div",
    "ui-state ui-state--empty"
  );

  element.setAttribute(
    "role",
    "status"
  );

  element.textContent =
    message;

  return element;
}

export function createErrorState(
  message = "Unable to load data."
): HTMLElement {
  const element = el(
    "div",
    "ui-state ui-state--error"
  );

  element.setAttribute(
    "role",
    "alert"
  );

  element.textContent =
    message;

  return element;
}

export function createLoadingState(
  message = "Loading…"
): HTMLElement {
  const element = el(
    "div",
    "ui-state ui-state--loading"
  );

  element.setAttribute(
    "role",
    "status"
  );

  element.setAttribute(
    "aria-live",
    "polite"
  );

  element.textContent =
    message;

  return element;
}