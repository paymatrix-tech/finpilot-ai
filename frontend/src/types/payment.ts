export type Payment = {
  id: string;
  customer_id: string;
  amount: string;
  currency: string;
  payment_method: string;
  status: string;
  gateway: string;
  error_code: string | null;
  created_at: string;
  updated_at: string;
};

export type PaymentListResponse = {
  items: Payment[];
};
