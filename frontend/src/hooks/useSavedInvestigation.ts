import { useQuery } from "@tanstack/react-query";
import { fetchInvestigation } from "../api/investigations";

export function useSavedInvestigation(investigationId: number | undefined) {
  return useQuery({
    queryKey: ["investigation", investigationId],
    queryFn: () => fetchInvestigation(investigationId!),
    enabled: investigationId !== undefined && !Number.isNaN(investigationId),
  });
}
