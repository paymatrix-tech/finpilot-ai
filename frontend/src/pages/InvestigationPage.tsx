import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { DEFAULT_QUESTION } from "../api/investigations";
import { InvestigationErrorAlert } from "../components/investigation/InvestigationErrorAlert";
import { InvestigationHistory } from "../components/investigation/InvestigationHistory";
import { InvestigationProgress } from "../components/investigation/InvestigationProgress";
import { InvestigationResults } from "../components/investigation/InvestigationResults";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { BackLink } from "../components/ui/BackLink";
import { EmptyState } from "../components/ui/EmptyState";
import { PageHeader } from "../components/ui/PageHeader";
import { PanelSkeleton } from "../components/ui/PanelSkeleton";
import { pageStackClass, panelClass, panelPaddingClass } from "../components/ui/classes";
import { useInvestigation } from "../hooks/useInvestigation";
import { useInvestigationHistory } from "../hooks/useInvestigationHistory";
import { useInvestigationProgress } from "../hooks/useInvestigationProgress";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { isApiErrorCode } from "../lib/apiErrors";
import { formatAmount } from "../lib/format";

export function InvestigationPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const autoStarted = useRef(false);

  const { payment, isPaymentPending, notFound } = usePaymentDetail(paymentId);
  const historyQuery = useInvestigationHistory(paymentId);
  const {
    mutate: runInvestigation,
    isPending: isRunning,
    data: result,
    isError,
    error,
    liveSteps,
    rcaPhase,
  } = useInvestigation();

  const { steps: progressSteps, isLive: progressIsLive } = useInvestigationProgress(
    isRunning,
    result?.steps,
    {
      steps: liveSteps,
      rcaPhase,
      started: isRunning || liveSteps.length > 0,
    },
  );

  useEffect(() => {
    if (!paymentId || autoStarted.current) {
      return;
    }
    autoStarted.current = true;
    runInvestigation({ paymentId, question: DEFAULT_QUESTION });
  }, [paymentId, runInvestigation]);

  if (!paymentId) {
    return (
      <EmptyState
        title="Missing payment ID"
        description="Start an investigation from a payment in the ledger."
        action={<BackLink to="/">← Back to payments</BackLink>}
      />
    );
  }

  const resolvedPaymentId = paymentId;
  const detailHref = `/payments/${encodeURIComponent(resolvedPaymentId)}`;

  function handleRerun(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isRunning) {
      return;
    }
    runInvestigation({ paymentId: resolvedPaymentId, question: trimmed });
  }

  const savedHref =
    result?.id != null
      ? `/payments/${encodeURIComponent(resolvedPaymentId)}/investigations/${result.id}`
      : null;

  const paymentMeta =
    payment && !isPaymentPending
      ? `${formatAmount(payment.amount, payment.currency)} via ${payment.gateway}${
          payment.error_code ? ` · error ${payment.error_code}` : ""
        }`
      : undefined;

  return (
    <div className={pageStackClass}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <BackLink to={detailHref}>← Back to payment details</BackLink>
        {payment && <PaymentStatusBadge status={payment.status} />}
      </div>

      <PageHeader
        eyebrow="AI investigation"
        title="Why did this payment fail?"
        description="FinPilot gathers payment data, events, logs, and documentation, then explains the likely root cause."
        meta={
          <>
            <p className="font-mono text-[13px]">{paymentId}</p>
            {paymentMeta && <p className="mt-1">{paymentMeta}</p>}
          </>
        }
      />

      {isPaymentPending && (
        <div className={`${panelClass} ${panelPaddingClass}`} aria-busy="true">
          <PanelSkeleton lines={4} />
        </div>
      )}

      {!isPaymentPending && notFound && (
        <EmptyState
          monoHint={paymentId}
          title="Payment not found"
          description="This payment is not in the ledger, so FinPilot cannot investigate it."
          action={<BackLink to="/">Search the ledger</BackLink>}
        />
      )}

      {!notFound && (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
          <div className="space-y-6">
            <form
              onSubmit={handleRerun}
              className={`${panelClass} ${panelPaddingClass}`}
            >
              <label className="block text-sm font-semibold text-ink" htmlFor="investigation-question">
                Investigation question
              </label>
              <p className="mt-1 text-sm text-muted">
                Adjust the question before re-running. The first investigation starts automatically.
              </p>
              <textarea
                id="investigation-question"
                rows={2}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                disabled={isRunning}
                className="mt-4 w-full resize-y rounded-2xl border border-line bg-page px-4 py-3 text-sm text-ink outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20 disabled:opacity-60"
              />
              <div className="mt-4">
                <button
                  type="submit"
                  disabled={isRunning || !question.trim()}
                  className="inline-flex items-center justify-center rounded-full bg-accent px-5 py-2.5 text-sm font-semibold text-panel transition hover:bg-[#0c4a45] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isRunning ? "Investigating…" : result ? "Run again" : "Investigate"}
                </button>
              </div>
            </form>

            {(isRunning || (result && progressSteps.length > 0)) && (
              <InvestigationProgress steps={progressSteps} isLive={progressIsLive} />
            )}

            {isError && (
              <InvestigationErrorAlert
                error={error}
                footer={
                  isApiErrorCode(error, "payment_not_found") ? (
                    <BackLink to="/">Search the ledger</BackLink>
                  ) : undefined
                }
              />
            )}

            {result && !isRunning && (
              <div className="space-y-6">
                {savedHref && (
                  <p className="rounded-2xl border border-line bg-page px-4 py-3 text-sm text-muted">
                    Saved as investigation #{result.id}.{" "}
                    <Link
                      to={savedHref}
                      className="font-medium text-accent no-underline hover:underline"
                    >
                      Open saved copy
                    </Link>
                  </p>
                )}
                <InvestigationResults
                  data={{
                    question: result.question,
                    root_cause: result.root_cause,
                    confidence: result.confidence,
                    evidence: result.evidence,
                    recommendation: result.recommendation,
                    sources: result.sources,
                    model: result.model,
                    provider: result.provider,
                    insufficient_evidence: result.insufficient_evidence,
                  }}
                />
              </div>
            )}
          </div>

          <aside>
            <InvestigationHistory
              paymentId={resolvedPaymentId}
              items={historyQuery.data ?? []}
              isLoading={historyQuery.isPending}
              isError={historyQuery.isError}
              error={historyQuery.error}
              activeInvestigationId={result?.id ?? undefined}
            />
          </aside>
        </div>
      )}
    </div>
  );
}
