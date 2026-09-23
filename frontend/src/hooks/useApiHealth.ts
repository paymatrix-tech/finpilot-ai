import { useQuery } from "@tanstack/react-query";
import { checkApiHealth } from "../api/client";

export function useApiHealth() {
  return useQuery({
    queryKey: ["api-health"],
    queryFn: checkApiHealth,
    staleTime: 30_000,
    retry: 1,
  });
}
