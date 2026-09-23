import { useQueries } from "@tanstack/react-query";
import { ApiError } from "../api/client";
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
  const paymentError = paymentQuery.error;
  const notFound =
    paymentError instanceof ApiError && paymentError.status === 404;

  return {
    payment: paymentQuery.data,
    events: eventsQuery.data?.items ?? [],
    logs: logsQuery.data?.items ?? [],
    isPaymentPending: paymentQuery.isPending,
    isEventsPending: eventsQuery.isPending,
    isLogsPending: logsQuery.isPending,
    notFound,
    paymentError,
    eventsError: eventsQuery.error,
    logsError: logsQuery.error,
  };
}
