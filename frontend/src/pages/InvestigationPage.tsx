import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError } from "../api/client";
import { DEFAULT_QUESTION } from "../api/investigations";
import { ConfidenceBadge } from "../components/investigation/ConfidenceBadge";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { useInvestigation } from "../hooks/useInvestigation";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { formatAmount } from "../lib/format";

function errorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Request failed";
}

function InvestigationSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-8 w-2/3 rounded-lg bg-line/60" />
      <div className="h-24 rounded-3xl bg-line/40" />
      <div className="h-32 rounded-3xl bg-line/40" />
      <div className="h-20 rounded-3xl bg-line/30" />
    </div>
  );
}

export function InvestigationPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const [question, setQuestion] = useState(DEFAULT_QUESTION);
  const autoStarted = useRef(false);

  const { payment, isPaymentPending, notFound } = usePaymentDetail(paymentId);
  const {
    mutate: runInvestigation,
    isPending: isRunning,
    data: result,
    isError,
    error,
  } = useInvestigation();

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

      {isPaymentPending && <InvestigationSkeleton />}

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
        <>
          <form
            onSubmit={handleRerun}
            className="rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_60px_rgba(28,25,21,0.04)] sm:p-6"
          >
            <label className="block text-sm font-semibold text-ink" htmlFor="investigation-question">
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
              {isRunning && (
                <p className="text-sm text-muted">This may take a moment while tools run.</p>
              )}
            </div>
          </form>

          {isError && (
            <div className="rounded-3xl border border-danger/30 bg-danger-soft px-5 py-4 text-sm text-danger">
              Investigation failed. {errorMessage(error)}
            </div>
          )}

          {isRunning && !result && <InvestigationSkeleton />}

          {result && !isRunning && (
            <div className="space-y-6">
              <section
                className="rounded-3xl border border-accent/25 bg-accent-soft/40 p-5 sm:p-6"
                aria-labelledby="root-cause-heading"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <h2 id="root-cause-heading" className="text-sm font-semibold tracking-wide text-ink">
                    Root cause
                  </h2>
                  <ConfidenceBadge confidence={result.confidence} />
                </div>
                <p className="mt-3 text-lg font-medium leading-relaxed text-ink">
                  {result.root_cause}
                </p>
              </section>

              <section
                className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
                aria-labelledby="question-heading"
              >
                <h2 id="question-heading" className="text-sm font-semibold tracking-wide text-ink">
                  Question
                </h2>
                <p className="mt-3 text-base text-ink">{result.question}</p>
              </section>

              <section
                className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
                aria-labelledby="evidence-heading"
              >
                <h2 id="evidence-heading" className="text-sm font-semibold tracking-wide text-ink">
                  Evidence
                </h2>
                {result.evidence.length === 0 ? (
                  <p className="mt-3 text-sm text-muted">No evidence items were returned.</p>
                ) : (
                  <ul className="mt-4 list-none space-y-2 p-0">
                    {result.evidence.map((item, index) => (
                      <li
                        key={`${index}-${item.slice(0, 24)}`}
                        className="flex gap-3 text-sm leading-relaxed text-ink"
                      >
                        <span
                          aria-hidden
                          className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                        />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {result.sources.length > 0 && (
                  <div className="mt-5 border-t border-line pt-4">
                    <p className="text-xs font-semibold tracking-wide text-muted uppercase">
                      Documentation sources
                    </p>
                    <ul className="mt-2 flex flex-wrap gap-2">
                      {result.sources.map((source) => (
                        <li
                          key={source}
                          className="rounded-full bg-page px-3 py-1 font-mono text-xs text-muted"
                        >
                          {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>

              <section
                className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
                aria-labelledby="recommendation-heading"
              >
                <h2
                  id="recommendation-heading"
                  className="text-sm font-semibold tracking-wide text-ink"
                >
                  Recommendation
                </h2>
                <p className="mt-3 text-base leading-relaxed text-ink">{result.recommendation}</p>
              </section>

              <p className="text-center text-xs text-muted">
                Model {result.model} ({result.provider})
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
