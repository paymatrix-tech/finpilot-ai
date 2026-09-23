import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { fetchPayments } from "../api/payments";

export function usePayments(query: string) {
  return useQuery({
    queryKey: ["payments", query],
    queryFn: () => fetchPayments(query),
    placeholderData: keepPreviousData,
  });
}
