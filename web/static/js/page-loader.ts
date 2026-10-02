import { getErrorMessage } from "./page-state";

export type LoaderStatus =
  | "loading"
  | "ready"
  | "error";

export interface LoaderContext<T> {
  data: T | null;
  status: LoaderStatus;
  error: string | null;
}

export interface PageLoader<T> {
  load(): Promise<LoaderContext<T>>;
  getState(): LoaderContext<T>;
}

export type LoaderFn<T> = () => Promise<T>;

export interface RenderTargets {
  loading?: HTMLElement | null;
  content?: HTMLElement | null;
  error?: HTMLElement | null;
}

function show(
  element: HTMLElement | null | undefined,
  visible: boolean
): void {
  if (element) {
    element.hidden = !visible;
  }
}

export function createPageLoader<T>(
  loader: LoaderFn<T>,
  targets: RenderTargets = {}
): PageLoader<T> {
  let context: LoaderContext<T> = {
    data: null,
    status: "loading",
    error: null
  };

  async function load(): Promise<LoaderContext<T>> {
    context = {
      data: null,
      status: "loading",
      error: null
    };

    show(targets.loading, true);
    show(targets.error, false);

    if (targets.content) {
      targets.content.dataset.state = "loading";
    }

    try {
      const data = await loader();

      context = {
        data,
        status: "ready",
        error: null
      };

      show(targets.loading, false);
      show(targets.error, false);
      show(targets.content, true);

      if (targets.content) {
        targets.content.dataset.state = "ready";
      }

      return context;
    } catch (error: unknown) {
      const message = getErrorMessage(error);

      context = {
        data: null,
        status: "error",
        error: message
      };

      show(targets.loading, false);
      show(targets.content, false);
      show(targets.error, true);

      if (targets.error) {
        targets.error.textContent = message;
        targets.error.dataset.state = "error";
      }

      if (targets.content) {
        targets.content.dataset.state = "error";
      }

      return context;
    }
  }

  return {
    load,
    getState: () => context
  };
}