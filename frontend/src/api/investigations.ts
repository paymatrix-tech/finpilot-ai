import { getJson, postJson } from "./client";
import type {
  CreateInvestigationRequest,
  InvestigationListResponse,
  InvestigationResult,
  SavedInvestigation,
} from "../types/investigation";

const DEFAULT_QUESTION = "Why did this payment fail?";

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
