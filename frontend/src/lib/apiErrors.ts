import { ApiError } from "../api/client";

export type ApiErrorCode =
  | "payment_not_found"
  | "database_error"
  | "llm_unavailable"
  | "llm_request_failed"
  | "llm_rate_limited"
  | "investigation_not_found"
  | "unknown";

export type ApiErrorPresentation = {
  title: string;
  message: string;
  suggestion?: string;
};

const PRESENTATIONS: Record<ApiErrorCode, ApiErrorPresentation> = {
  payment_not_found: {
    title: "Payment not found",
    message: "This payment ID is not in the ledger.",
    suggestion: "Return to search and pick a payment from the list.",
  },
  database_error: {
    title: "Database unavailable",
    message: "FinPilot could not read or save investigation data.",
    suggestion: "Check that PostgreSQL is running, then try again.",
  },
  llm_unavailable: {
    title: "AI model not configured",
    message: "The investigation service is not connected to a language model.",
    suggestion: "Verify LLM settings in the API environment and restart the backend.",
  },
  llm_request_failed: {
    title: "AI model request failed",
    message: "The model could not complete this investigation.",
    suggestion: "Wait a moment and run the investigation again.",
  },
  llm_rate_limited: {
    title: "AI rate limit reached",
    message: "The provider temporarily blocked new requests.",
    suggestion:
      "Gemini free tier allows only a few requests per minute, and each investigation uses multiple calls. Wait about a minute, use LLM_PROVIDER=stub locally, or upgrade billing.",
  },
  investigation_not_found: {
    title: "Investigation not found",
    message: "This saved investigation no longer exists.",
    suggestion: "Run a new investigation from the payment page.",
  },
  unknown: {
    title: "Something went wrong",
    message: "The request could not be completed.",
    suggestion: "Try again or refresh the page.",
  },
};

export function normalizeApiErrorCode(code: string | undefined): ApiErrorCode {
  if (code && code in PRESENTATIONS) {
    return code as ApiErrorCode;
  }
  return "unknown";
}

export function presentApiError(error: unknown): ApiErrorPresentation {
  if (error instanceof ApiError) {
    const code = normalizeApiErrorCode(error.code);
    const base = PRESENTATIONS[code];
    const retryHint =
      error.retryAfterSeconds !== undefined
        ? `Suggested wait: about ${error.retryAfterSeconds} seconds.`
        : undefined;
    return {
      ...base,
      message: error.message || base.message,
      suggestion: [retryHint, base.suggestion].filter(Boolean).join(" "),
    };
  }
  if (error instanceof Error) {
    return { ...PRESENTATIONS.unknown, message: error.message };
  }
  return PRESENTATIONS.unknown;
}

export function isApiErrorCode(error: unknown, code: ApiErrorCode): boolean {
  return error instanceof ApiError && normalizeApiErrorCode(error.code) === code;
}
