import { useQuery } from "@tanstack/react-query";
import { fetchPaymentInvestigations } from "../api/investigations";

export function useInvestigationHistory(paymentId: string | undefined) {
  return useQuery({
    queryKey: ["investigations", paymentId],
    queryFn: () => fetchPaymentInvestigations(paymentId!),
    enabled: Boolean(paymentId),
    select: (data) => data.items,
  });
}
