import { useMutation } from "@tanstack/react-query";
import { createInvestigation } from "../api/investigations";

export function useInvestigation() {
  return useMutation({
    mutationFn: ({ paymentId, question }: { paymentId: string; question: string }) =>
      createInvestigation(paymentId, question),
  });
}
