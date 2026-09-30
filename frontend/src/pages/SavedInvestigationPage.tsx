import { useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { InvestigationErrorAlert } from "../components/investigation/InvestigationErrorAlert";
import { InvestigationHistory } from "../components/investigation/InvestigationHistory";
import { InvestigationResults } from "../components/investigation/InvestigationResults";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { BackLink } from "../components/ui/BackLink";
import { EmptyState } from "../components/ui/EmptyState";
import { PageHeader } from "../components/ui/PageHeader";
import { PanelSkeleton } from "../components/ui/PanelSkeleton";
import { pageStackClass, panelClass, panelPaddingClass } from "../components/ui/classes";
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
    return (
      <EmptyState
        title="Invalid investigation link"
        description="Use a saved investigation from the history list or run a new investigation."
        action={<BackLink to="/">← Back to payments</BackLink>}
      />
    );
  }

  const investigateHref = `/payments/${encodeURIComponent(paymentId)}/investigate`;
  const detailHref = `/payments/${encodeURIComponent(paymentId)}`;
  const notFound =
    savedQuery.error instanceof ApiError && savedQuery.error.status === 404;

  return (
    <div className={pageStackClass}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <BackLink to={investigateHref}>← New investigation</BackLink>
        {payment && <PaymentStatusBadge status={payment.status} />}
      </div>

      <PageHeader
        eyebrow="Saved investigation"
        title={`Investigation #${validId}`}
        meta={
          <>
            <p className="font-mono text-[13px]">{paymentId}</p>
            {savedQuery.data && (
              <p className="mt-1">Run at {formatDateTime(savedQuery.data.created_at)}</p>
            )}
            {payment && !isPaymentPending && (
              <p className="mt-1">
                {formatAmount(payment.amount, payment.currency)} via {payment.gateway}
              </p>
            )}
          </>
        }
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
        <div>
          {savedQuery.isPending && (
            <div className={`${panelClass} ${panelPaddingClass}`} aria-busy="true">
              <PanelSkeleton lines={5} />
            </div>
          )}

          {notFound && (
            <EmptyState
              title="Investigation not found"
              description="It may have been removed or the link is outdated."
              action={<BackLink to={investigateHref}>Start a new investigation</BackLink>}
            />
          )}

          {savedQuery.isError && !notFound && (
            <InvestigationErrorAlert
              error={savedQuery.error}
              footer={
                isApiErrorCode(savedQuery.error, "database_error") ? (
                  <p className="text-xs text-muted">
                    The API health indicator in the header shows database status.
                  </p>
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
            isError={historyQuery.isError}
            error={historyQuery.error}
            activeInvestigationId={validId}
          />
          <p className="text-center">
            <BackLink to={detailHref}>View payment details</BackLink>
          </p>
        </aside>
      </div>

      {!isPaymentPending && paymentNotFound && (
        <p className="text-sm text-copper">Payment record is no longer available.</p>
      )}
    </div>
  );
}
