const API_BASE =
  (import.meta as unknown as { env?: { VITE_API_BASE_URL?: string } })
    .env?.VITE_API_BASE_URL ?? "";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export function isApiError(value: unknown): value is ApiError {
  return value instanceof ApiError;
}

function extractMessage(body: unknown, status: number): string {
  if (typeof body === "string" && body.trim()) return body;

  if (body && typeof body === "object") {
    const obj = body as Record<string, unknown>;

    /* FastAPI standard: { detail: "string" } */
    if (typeof obj.detail === "string") return obj.detail;

    /* FastAPI validation: { detail: [{loc, msg, type}] } */
    if (Array.isArray(obj.detail)) {
      const lines = obj.detail
        .map((item) => {
          if (item && typeof item === "object") {
            const it = item as Record<string, unknown>;
            const loc = Array.isArray(it.loc)
              ? it.loc.join(".")
              : String(it.loc ?? "");
            const msg = String(it.msg ?? "invalid");
            return loc ? `${loc}: ${msg}` : msg;
          }
          return String(item);
        })
        .filter(Boolean);

      if (lines.length) {
        return lines.join(" · ");
      }
    }

    if (typeof obj.message === "string") return obj.message;
    if (typeof obj.error === "string") return obj.error;
  }

  return `Request failed: ${status}`;
}

export function getApiErrorMessage(
  error: unknown,
  fallback = "Request failed.",
): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return fallback;
}

async function parseBody(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function buildUrl(path: string): string {
  if (!API_BASE) return path;
  return `${API_BASE}${path}`;
}

export async function get<T = unknown>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: "GET",
    headers: {
      Accept: "application/json",
      ...(init?.headers || {}),
    },
    ...init,
  });

  const body = await parseBody(res);

  if (!res.ok) {
    throw new ApiError(
      extractMessage(body, res.status),
      res.status,
      body,
    );
  }

  return body as T;
}

export async function post<T = unknown>(
  path: string,
  payload?: unknown,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(buildUrl(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init?.headers || {}),
    },
    body: payload !== undefined ? JSON.stringify(payload) : undefined,
    ...init,
  });

  const body = await parseBody(res);

  if (!res.ok) {
    throw new ApiError(
      extractMessage(body, res.status),
      res.status,
      body,
    );
  }

  return body as T;
}

export const apiGet = get;
export const apiPost = post;