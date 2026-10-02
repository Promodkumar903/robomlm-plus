export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string
): HTMLElementTagNameMap[K] {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  return element;
}

export function text(
  value: unknown
): Text {
  return document.createTextNode(
    value == null ? "—" : String(value)
  );
}

export function clear(
  element: HTMLElement
): void {
  element.replaceChildren();
}

export function mount(
  target: HTMLElement,
  element: HTMLElement
): void {
  target.appendChild(element);
}

export function setText(
  target: HTMLElement,
  value: unknown
): void {
  target.textContent =
    value == null ? "—" : String(value);
}