import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { streamInvestigation } from "../api/investigations";
import type { ToolExecutionStep } from "../types/investigation";

export function useInvestigation() {
  const queryClient = useQueryClient();
  const [liveSteps, setLiveSteps] = useState<ToolExecutionStep[]>([]);
  const [rcaPhase, setRcaPhase] = useState(false);

  const mutation = useMutation({
    mutationFn: async ({ paymentId, question }: { paymentId: string; question: string }) => {
      setLiveSteps([]);
      setRcaPhase(false);
      return streamInvestigation(paymentId, question, {
        onToolStep: (step) => {
          setLiveSteps((previous) => [...previous, step]);
        },
        onRcaStarted: () => {
          setRcaPhase(true);
        },
      });
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["investigations", variables.paymentId] });
    },
    onSettled: () => {
      setRcaPhase(false);
    },
  });

  return {
    ...mutation,
    liveSteps,
    rcaPhase,
  };
}
