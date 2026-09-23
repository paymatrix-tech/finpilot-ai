import { getJson } from "./client";
import type { PaymentListResponse } from "../types/payment";

export async function fetchPayments(query: string): Promise<PaymentListResponse> {
  const params = new URLSearchParams({ limit: "50" });
  if (query.trim()) {
    params.set("q", query.trim());
  }
  return getJson<PaymentListResponse>(`/api/payments?${params.toString()}`);
}
