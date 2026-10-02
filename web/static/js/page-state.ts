import { ApiRequestError } from "./api-client";

export type PageState =
  | { status: "loading" }
  | { status: "ready" }
  | {
      status: "error";
      message: string;
      httpStatus?: number;
    };

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) {
    if (error.status === 401)
      return "Authentication required.";

    if (error.status === 403)
      return "Access denied.";

    if (error.status === 404)
      return "This backend route is not available.";

    if (error.status >= 500)
      return "Backend service error.";

    return error.message;
  }

  if (error instanceof Error)
    return error.message;

  return "Unexpected frontend error.";
}

export function setLoading(element: HTMLElement): void {
  element.dataset.state = "loading";
  element.textContent = "Loading…";
}

export function setError(
  element: HTMLElement,
  error: unknown
): void {
  element.dataset.state = "error";
  element.textContent = getErrorMessage(error);
}

export function setReady(element: HTMLElement): void {
  element.dataset.state = "ready";
}