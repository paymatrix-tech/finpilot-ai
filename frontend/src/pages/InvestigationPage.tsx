import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { DEFAULT_QUESTION } from "../api/investigations";
import { InvestigationErrorAlert } from "../components/investigation/InvestigationErrorAlert";
import { InvestigationHistory } from "../components/investigation/InvestigationHistory";
import { InvestigationProgress } from "../components/investigation/InvestigationProgress";
import { InvestigationResults } from "../components/investigation/InvestigationResults";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
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
  } = useInvestigation();

  const { steps: progressSteps, isLive: progressIsLive } = useInvestigationProgress(
    isRunning,
    result?.steps,
  );

  useEffect(() => {
    if (!paymentId || autoStarted.current) {
      return;
    }
    autoStarted.current = true;
    runInvestigation({ paymentId, question: DEFAULT_QUESTION });
  }, [paymentId, runInvestigation]);

  if (!paymentId) {
    return <p className="text-sm text-danger">Missing payment ID in the URL.</p>;
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

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Link
          to={detailHref}
          className="text-sm font-medium text-accent no-underline hover:underline"
        >
          ← Back to payment details
        </Link>
        {payment && <PaymentStatusBadge status={payment.status} />}
      </div>

      <header className="space-y-3">
        <p className="text-xs font-semibold tracking-[0.16em] text-muted uppercase">
          AI investigation
        </p>
        <h1 className="font-display text-3xl tracking-tight sm:text-4xl">
          Why did this payment fail?
        </h1>
        <p className="font-mono text-sm text-muted">{paymentId}</p>
        {payment && !isPaymentPending && (
          <p className="text-sm text-muted">
            {formatAmount(payment.amount, payment.currency)} via {payment.gateway}
            {payment.error_code ? (
              <>
                {" "}
                · error{" "}
                <span className="font-mono text-copper">{payment.error_code}</span>
              </>
            ) : null}
          </p>
        )}
      </header>

      {isPaymentPending && (
        <div className="animate-pulse rounded-3xl border border-line bg-panel p-6">
          <div className="h-4 w-40 rounded bg-line/60" />
          <div className="mt-6 space-y-4">
            <div className="h-4 w-3/4 rounded bg-line/40" />
            <div className="h-4 w-2/3 rounded bg-line/30" />
          </div>
        </div>
      )}

      {!isPaymentPending && notFound && (
        <div className="rounded-3xl border border-line bg-panel px-6 py-10 text-center">
          <p className="font-mono text-lg">{paymentId}</p>
          <p className="mt-2 text-sm text-muted">No payment exists with that ID.</p>
          <Link
            to="/"
            className="mt-4 inline-block text-sm font-medium text-accent no-underline hover:underline"
          >
            Search the ledger
          </Link>
        </div>
      )}

      {!notFound && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(280px,340px)]">
          <div className="space-y-6">
            <form
              onSubmit={handleRerun}
              className="rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_60px_rgba(28,25,21,0.04)] sm:p-6"
            >
              <label
                className="block text-sm font-semibold text-ink"
                htmlFor="investigation-question"
              >
                Investigation question
              </label>
              <p className="mt-1 text-sm text-muted">
                FinPilot reads payment data, events, logs, and internal docs to answer this.
              </p>
              <textarea
                id="investigation-question"
                rows={2}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                disabled={isRunning}
                className="mt-4 w-full resize-y rounded-2xl border border-line bg-page px-4 py-3 text-sm text-ink outline-none transition focus:border-accent focus:ring-2 focus:ring-accent/20 disabled:opacity-60"
              />
              <div className="mt-4 flex flex-wrap items-center gap-3">
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
                    <Link
                      to="/"
                      className="text-sm font-medium text-accent no-underline hover:underline"
                    >
                      Search the ledger
                    </Link>
                  ) : undefined
                }
              />
            )}

            {result && !isRunning && (
              <>
                {savedHref && (
                  <p className="text-sm text-muted">
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
              </>
            )}
          </div>

          <aside>
            <InvestigationHistory
              paymentId={resolvedPaymentId}
              items={historyQuery.data ?? []}
              isLoading={historyQuery.isPending}
              activeInvestigationId={result?.id ?? undefined}
            />
          </aside>
        </div>
      )}
    </div>
  );
}
