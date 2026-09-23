import type { Payment } from "./payment";

export type PaymentEvent = {
  id: number;
  payment_id: string;
  event_type: string;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type PaymentLog = {
  id: number;
  payment_id: string;
  service: string;
  level: string;
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type PaymentEventListResponse = {
  items: PaymentEvent[];
};

export type PaymentLogListResponse = {
  items: PaymentLog[];
};

export type PaymentDetailData = {
  payment: Payment;
  events: PaymentEvent[];
  logs: PaymentLog[];
};
