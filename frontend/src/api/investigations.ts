import { postJson } from "./client";
import type { CreateInvestigationRequest, InvestigationResult } from "../types/investigation";

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

export { DEFAULT_QUESTION };
