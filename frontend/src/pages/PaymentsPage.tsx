import { useState } from "react";
import { PaymentSearch } from "../components/payments/PaymentSearch";
import { PaymentTable } from "../components/payments/PaymentTable";
import { PaymentTableSkeleton } from "../components/payments/PaymentTableSkeleton";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { usePayments } from "../hooks/usePayments";

export function PaymentsPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const debouncedQuery = useDebouncedValue(query);
  const activeQuery = submittedQuery ?? debouncedQuery;
  const paymentsQuery = usePayments(activeQuery);
  const count = paymentsQuery.data?.items.length ?? 0;

  return (
    <div className="space-y-6">
      <section className="max-w-2xl">
        <h1 className="font-display text-4xl leading-tight font-medium tracking-tight sm:text-[2.6rem]">
          Find why a payment failed.
        </h1>
        <p className="mt-2 max-w-lg text-[15px] text-muted">
          Search the ledger by payment ID, gateway, or error code.
        </p>
      </section>

      <PaymentSearch
        value={query}
        onChange={(value) => {
          setSubmittedQuery(null);
          setQuery(value);
        }}
        onSubmit={() => setSubmittedQuery(query)}
      />

      <section
        aria-live="polite"
        className="overflow-x-auto rounded-3xl border border-line bg-panel shadow-[0_24px_60px_rgba(28,25,21,0.06)]"
      >
        <div className="flex items-end justify-between gap-4 border-b border-line px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold">Recent payments</h2>
            <p className="text-xs text-muted">
              {paymentsQuery.isPending
                ? "Loading ledger…"
                : `${count} ${count === 1 ? "result" : "results"}`}
            </p>
          </div>
        </div>

        {paymentsQuery.isPending && <PaymentTableSkeleton />}
        {paymentsQuery.isError && !paymentsQuery.data && (
          <p className="px-5 py-8 text-sm text-danger">
            Could not load payments.{" "}
            {paymentsQuery.error instanceof Error
              ? paymentsQuery.error.message
              : "Request failed"}
          </p>
        )}
        {paymentsQuery.data?.items.length === 0 && (
          <p className="px-5 py-10 text-center text-sm text-muted">
            No payments matched that search.
          </p>
        )}
        {!!paymentsQuery.data?.items.length && (
          <PaymentTable payments={paymentsQuery.data.items} />
        )}
      </section>
    </div>
  );
}
