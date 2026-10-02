export interface RenderContext {
  root: HTMLElement;
}

export interface PageRenderer<T> {
  render(data: T, context: RenderContext): void | Promise<void>;
}

export function getRenderContext(): RenderContext {
  const root = document.querySelector<HTMLElement>(
    "#page-content"
  );

  if (!root) {
    throw new Error(
      "Page content root #page-content was not found."
    );
  }

  return { root };
}

export function text(
  elementId: string,
  value: unknown
): void {
  const element =
    document.getElementById(elementId);

  if (!element) return;

  element.textContent =
    value == null
      ? "—"
      : String(value);
}

export function json(
  elementId: string,
  value: unknown
): void {
  const element =
    document.getElementById(elementId);

  if (!element) return;

  element.textContent = JSON.stringify(
    value,
    null,
    2
  );
}

export function clear(
  elementId: string
): void {
  const element =
    document.getElementById(elementId);

  if (!element) return;

  element.replaceChildren();
}