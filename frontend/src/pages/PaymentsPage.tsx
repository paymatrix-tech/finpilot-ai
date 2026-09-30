import { useState } from "react";
import { PaymentSearch } from "../components/payments/PaymentSearch";
import { PaymentTable } from "../components/payments/PaymentTable";
import { PaymentTableSkeleton } from "../components/payments/PaymentTableSkeleton";
import { EmptyState } from "../components/ui/EmptyState";
import { PageHeader } from "../components/ui/PageHeader";
import { QueryErrorAlert } from "../components/ui/QueryErrorAlert";
import { panelClass, pageStackClass } from "../components/ui/classes";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { usePayments } from "../hooks/usePayments";

export function PaymentsPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string | null>(null);
  const debouncedQuery = useDebouncedValue(query);
  const activeQuery = submittedQuery ?? debouncedQuery;
  const paymentsQuery = usePayments(activeQuery);
  const count = paymentsQuery.data?.items.length ?? 0;
  const hasSearch = activeQuery.trim().length > 0;

  return (
    <div className={pageStackClass}>
      <PageHeader
        title="Find why a payment failed."
        description="Search the ledger by payment ID, gateway, error code, or customer ID."
      />

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
        className={`overflow-x-auto ${panelClass} shadow-[0_24px_60px_rgba(28,25,21,0.06)]`}
      >
        <div className="flex items-end justify-between gap-4 border-b border-line px-5 py-4 sm:px-6">
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-ink">Recent payments</h2>
            <p className="mt-0.5 text-xs text-muted">
              {paymentsQuery.isPending
                ? "Loading ledger…"
                : `${count} ${count === 1 ? "payment" : "payments"}`}
            </p>
          </div>
        </div>

        {paymentsQuery.isPending && <PaymentTableSkeleton />}
        {paymentsQuery.isError && !paymentsQuery.data && (
          <div className="p-5 sm:p-6">
            <QueryErrorAlert error={paymentsQuery.error} />
          </div>
        )}
        {!paymentsQuery.isPending &&
          !paymentsQuery.isError &&
          paymentsQuery.data?.items.length === 0 && (
            <div className="p-5 sm:p-6">
              <EmptyState
                compact
                title={hasSearch ? "No matching payments" : "No payments in the ledger"}
                description={
                  hasSearch
                    ? "Try a different ID fragment, gateway name, or error code."
                    : "Seed the database or adjust your search to explore sample payments."
                }
                action={
                  hasSearch ? (
                    <button
                      type="button"
                      className="text-sm font-medium text-accent"
                      onClick={() => {
                        setQuery("");
                        setSubmittedQuery("");
                      }}
                    >
                      Clear search
                    </button>
                  ) : undefined
                }
              />
            </div>
          )}
        {!!paymentsQuery.data?.items.length && (
          <PaymentTable payments={paymentsQuery.data.items} />
        )}
      </section>
    </div>
  );
}
