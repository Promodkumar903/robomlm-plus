export function text(
  elementId: string,
  value: unknown
): void {
  const element =
    document.getElementById(elementId);

  if (!element) return;

  element.textContent =
    value == null
      ? "-"
      : String(value);
}

export function json(
  elementId: string,
  value: unknown
): void {
  const element =
    document.getElementById(elementId);

  if (!element) return;

  element.textContent =
    JSON.stringify(value, null, 2);
}