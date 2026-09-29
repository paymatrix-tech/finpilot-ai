/** Empty in dev uses the Vite proxy; set VITE_API_URL for direct API access. */
const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type ErrorDetailPayload = {
  code?: string;
  message?: string;
};

function parseErrorDetail(detail: unknown): { message: string; code?: string } {
  if (typeof detail === "string") {
    return { message: detail };
  }
  if (typeof detail === "object" && detail !== null) {
    const payload = detail as ErrorDetailPayload;
    if (typeof payload.message === "string") {
      return {
        message: payload.message,
        code: typeof payload.code === "string" ? payload.code : undefined,
      };
    }
  }
  return { message: "Request failed." };
}

async function readApiError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    const parsed = parseErrorDetail(body.detail);
    return new ApiError(
      parsed.message || `Request failed (${response.status})`,
      response.status,
      parsed.code,
    );
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
