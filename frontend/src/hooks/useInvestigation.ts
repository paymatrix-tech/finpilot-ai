import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createInvestigation } from "../api/investigations";

export function useInvestigation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ paymentId, question }: { paymentId: string; question: string }) =>
      createInvestigation(paymentId, question),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["investigations", variables.paymentId] });
    },
  });
}
