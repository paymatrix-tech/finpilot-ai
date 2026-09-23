import { getJson } from "./client";
import type { PaymentListResponse } from "../types/payment";
import type {
  PaymentEventListResponse,
  PaymentLogListResponse,
} from "../types/paymentDetail";
import type { Payment } from "../types/payment";

export async function fetchPayments(query: string): Promise<PaymentListResponse> {
  const params = new URLSearchParams({ limit: "50" });
  if (query.trim()) {
    params.set("q", query.trim());
  }
  return getJson<PaymentListResponse>(`/api/payments?${params.toString()}`);
}

export async function fetchPayment(paymentId: string): Promise<Payment> {
  return getJson<Payment>(`/api/payments/${encodeURIComponent(paymentId)}`);
}

export async function fetchPaymentEvents(paymentId: string): Promise<PaymentEventListResponse> {
  return getJson<PaymentEventListResponse>(
    `/api/payments/${encodeURIComponent(paymentId)}/events`,
  );
}

export async function fetchPaymentLogs(paymentId: string): Promise<PaymentLogListResponse> {
  return getJson<PaymentLogListResponse>(
    `/api/payments/${encodeURIComponent(paymentId)}/logs`,
  );
}
