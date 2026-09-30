/** Empty in dev uses the Vite proxy; set VITE_API_URL for direct API access. */
export const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly retryAfterSeconds?: number;

  constructor(
    message: string,
    status: number,
    code?: string,
    retryAfterSeconds?: number,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

type ErrorDetailPayload = {
  code?: string;
  message?: string;
  retry_after_seconds?: number;
};

export function parseErrorDetail(detail: unknown): {
  message: string;
  code?: string;
  retryAfterSeconds?: number;
} {
  if (typeof detail === "string") {
    return { message: detail };
  }
  if (typeof detail === "object" && detail !== null) {
    const payload = detail as ErrorDetailPayload;
    if (typeof payload.message === "string") {
      return {
        message: payload.message,
        code: typeof payload.code === "string" ? payload.code : undefined,
        retryAfterSeconds:
          typeof payload.retry_after_seconds === "number"
            ? payload.retry_after_seconds
            : undefined,
      };
    }
  }
  return { message: "Request failed." };
}

export function apiErrorFromDetail(
  detail: unknown,
  status = 500,
): ApiError {
  const parsed = parseErrorDetail(detail);
  return new ApiError(
    parsed.message || `Request failed (${status})`,
    status,
    parsed.code,
    parsed.retryAfterSeconds,
  );
}

async function readApiError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    return apiErrorFromDetail(body.detail, response.status);
  } catch {
    return new ApiError(`Request failed (${response.status})`, response.status);
  }
}

export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw await readApiError(response);
  }
  return (await response.json()) as T;
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw await readApiError(response);
  }
  return (await response.json()) as T;
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      return false;
    }
    const body = (await response.json()) as { status?: string };
    return body.status === "ok";
  } catch {
    return false;
  }
}
