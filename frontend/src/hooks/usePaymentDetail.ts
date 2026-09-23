import { useQueries } from "@tanstack/react-query";
import { fetchPayment, fetchPaymentEvents, fetchPaymentLogs } from "../api/payments";

export function usePaymentDetail(paymentId: string | undefined) {
  const enabled = Boolean(paymentId);

  const results = useQueries({
    queries: [
      {
        queryKey: ["payment", paymentId],
        queryFn: () => fetchPayment(paymentId!),
        enabled,
      },
      {
        queryKey: ["payment-events", paymentId],
        queryFn: () => fetchPaymentEvents(paymentId!),
        enabled,
      },
      {
        queryKey: ["payment-logs", paymentId],
        queryFn: () => fetchPaymentLogs(paymentId!),
        enabled,
      },
    ],
  });

  const [paymentQuery, eventsQuery, logsQuery] = results;

  return {
    payment: paymentQuery.data,
    events: eventsQuery.data?.items ?? [],
    logs: logsQuery.data?.items ?? [],
    isPending: results.some((query) => query.isPending),
    isError: results.some((query) => query.isError),
    error: paymentQuery.error ?? eventsQuery.error ?? logsQuery.error,
  };
}
