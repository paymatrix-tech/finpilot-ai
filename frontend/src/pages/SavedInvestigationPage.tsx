import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { InvestigationErrorAlert } from "../components/investigation/InvestigationErrorAlert";
import { InvestigationHistory } from "../components/investigation/InvestigationHistory";
import { InvestigationResults } from "../components/investigation/InvestigationResults";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { useInvestigationHistory } from "../hooks/useInvestigationHistory";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { useSavedInvestigation } from "../hooks/useSavedInvestigation";
import { isApiErrorCode } from "../lib/apiErrors";
import { isInsufficientEvidence } from "../lib/investigationOutcome";
import { formatAmount, formatDateTime } from "../lib/format";

export function SavedInvestigationPage() {
  const { paymentId, investigationId: investigationIdParam } = useParams<{
    paymentId: string;
    investigationId: string;
  }>();
  const investigationId = investigationIdParam
    ? Number.parseInt(investigationIdParam, 10)
    : undefined;
  const validId =
    investigationId !== undefined && !Number.isNaN(investigationId) ? investigationId : undefined;

  const { payment, isPaymentPending, notFound: paymentNotFound } = usePaymentDetail(paymentId);
  const historyQuery = useInvestigationHistory(paymentId);
  const savedQuery = useSavedInvestigation(validId);

  if (!paymentId || validId === undefined) {
    return <p className="text-sm text-danger">Invalid investigation link.</p>;
  }

  const investigateHref = `/payments/${encodeURIComponent(paymentId)}/investigate`;
  const detailHref = `/payments/${encodeURIComponent(paymentId)}`;
  const notFound =
    savedQuery.error instanceof ApiError && savedQuery.error.status === 404;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          to={investigateHref}
          className="text-sm font-medium text-accent no-underline hover:underline"
        >
          ← New investigation
        </Link>
        {payment && <PaymentStatusBadge status={payment.status} />}
      </div>

      <header className="space-y-3">
        <p className="text-xs font-semibold tracking-[0.16em] text-muted uppercase">
          Saved investigation
        </p>
        <h1 className="font-display text-3xl tracking-tight sm:text-4xl">Investigation #{validId}</h1>
        <p className="font-mono text-sm text-muted">{paymentId}</p>
        {savedQuery.data && (
          <p className="text-sm text-muted">Run at {formatDateTime(savedQuery.data.created_at)}</p>
        )}
        {payment && !isPaymentPending && (
          <p className="text-sm text-muted">
            {formatAmount(payment.amount, payment.currency)} via {payment.gateway}
          </p>
        )}
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
        <div>
          {savedQuery.isPending && (
            <div className="animate-pulse rounded-3xl border border-line bg-panel p-6">
              <div className="h-4 w-40 rounded bg-line/60" />
              <div className="mt-6 h-24 rounded-2xl bg-line/40" />
            </div>
          )}

          {notFound && (
            <div className="rounded-3xl border border-line bg-panel px-6 py-10 text-center">
              <p className="text-sm text-muted">This investigation was not found.</p>
              <Link
                to={investigateHref}
                className="mt-4 inline-block text-sm font-medium text-accent no-underline hover:underline"
              >
                Start a new investigation
              </Link>
            </div>
          )}

          {savedQuery.isError && !notFound && (
            <InvestigationErrorAlert
              error={savedQuery.error}
              footer={
                isApiErrorCode(savedQuery.error, "database_error") ? (
                  <p className="text-xs text-muted">The API health indicator in the header shows database status.</p>
                ) : undefined
              }
            />
          )}

          {savedQuery.data && (
            <InvestigationResults
              data={{
                question: savedQuery.data.question,
                root_cause: savedQuery.data.root_cause ?? "Unknown",
                confidence: savedQuery.data.confidence ?? "low",
                evidence: savedQuery.data.evidence,
                recommendation: savedQuery.data.recommendation ?? "No recommendation recorded.",
                insufficient_evidence: isInsufficientEvidence(
                  savedQuery.data.root_cause,
                  savedQuery.data.confidence,
                  savedQuery.data.evidence,
                ),
              }}
            />
          )}
        </div>

        <aside className="space-y-4">
          <InvestigationHistory
            paymentId={paymentId}
            items={historyQuery.data ?? []}
            isLoading={historyQuery.isPending}
            activeInvestigationId={validId}
          />
          <Link
            to={detailHref}
            className="block text-center text-sm font-medium text-accent no-underline hover:underline"
          >
            View payment details
          </Link>
        </aside>
      </div>

      {!isPaymentPending && paymentNotFound && (
        <p className="text-sm text-copper">Payment record is no longer available.</p>
      )}
    </div>
  );
}
