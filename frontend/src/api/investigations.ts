import { API_BASE, ApiError, apiErrorFromDetail, getJson, postJson } from "./client";
import { readSseStream } from "./sse";
import type {
  CreateInvestigationRequest,
  InvestigationListResponse,
  InvestigationResult,
  SavedInvestigation,
  ToolExecutionStep,
} from "../types/investigation";

const DEFAULT_QUESTION = "Why did this payment fail?";

export type InvestigationStreamHandlers = {
  onStarted?: (data: { payment_id: string; question: string }) => void;
  onToolStep?: (step: ToolExecutionStep) => void;
  onRcaStarted?: () => void;
};

function parseApiErrorPayload(data: unknown): ApiError {
  if (typeof data === "object" && data !== null) {
    const error = apiErrorFromDetail(data, 429);
    if (error.message !== "Request failed.") {
      return error;
    }
  }
  return new ApiError("Investigation stream failed.", 500);
}

export async function streamInvestigation(
  paymentId: string,
  question: string,
  handlers: InvestigationStreamHandlers = {},
): Promise<InvestigationResult> {
  const body: CreateInvestigationRequest = {
    payment_id: paymentId,
    question,
  };

  const response = await fetch(`${API_BASE}/api/investigations/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    try {
      const json = JSON.parse(text) as { detail?: unknown };
      if (typeof json.detail === "object" && json.detail !== null) {
        throw parseApiErrorPayload(json.detail);
      }
      if (typeof json.detail === "string") {
        throw new ApiError(json.detail, response.status);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
    }
    throw new ApiError(`Request failed (${response.status})`, response.status);
  }

  let result: InvestigationResult | undefined;

  await readSseStream(response, ({ event, data }) => {
    if (event === "started" && typeof data === "object" && data !== null) {
      handlers.onStarted?.(data as { payment_id: string; question: string });
      return;
    }
    if (event === "tool_step") {
      handlers.onToolStep?.(data as ToolExecutionStep);
      return;
    }
    if (event === "rca_started") {
      handlers.onRcaStarted?.();
      return;
    }
    if (event === "complete") {
      result = data as InvestigationResult;
      return;
    }
    if (event === "error") {
      throw parseApiErrorPayload(data);
    }
  });

  if (!result) {
    throw new ApiError("Investigation ended without a result.", 500);
  }

  return result;
}

/** Non-streaming fallback (tests and simple clients). */
export function createInvestigation(
  paymentId: string,
  question = DEFAULT_QUESTION,
): Promise<InvestigationResult> {
  const body: CreateInvestigationRequest = {
    payment_id: paymentId,
    question,
  };
  return postJson<InvestigationResult>("/api/investigations", body);
}

export function fetchPaymentInvestigations(
  paymentId: string,
): Promise<InvestigationListResponse> {
  return getJson<InvestigationListResponse>(
    `/api/payments/${encodeURIComponent(paymentId)}/investigations`,
  );
}

export function fetchInvestigation(investigationId: number): Promise<SavedInvestigation> {
  return getJson<SavedInvestigation>(`/api/investigations/${investigationId}`);
}

export { DEFAULT_QUESTION };
