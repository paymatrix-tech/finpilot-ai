import { Link, useParams } from "react-router-dom";
import type { PropsWithChildren, ReactNode } from "react";
import { InvestigateButton } from "../components/payments/InvestigateButton";
import { PaymentEventsList } from "../components/payments/PaymentEventsList";
import { PaymentLogsList } from "../components/payments/PaymentLogsList";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { PaymentTimeline } from "../components/payments/PaymentTimeline";
import { ApiError } from "../api/client";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { formatAmount } from "../lib/format";

function DetailPanel({
  title,
  children,
  footer,
}: PropsWithChildren<{ title: string; footer?: ReactNode }>) {
  return (
    <section className="rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_60px_rgba(28,25,21,0.04)] sm:p-6">
      <h2 className="text-sm font-semibold tracking-wide text-ink">{title}</h2>
      <div className="mt-4">{children}</div>
      {footer}
    </section>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Request failed";
}

function PanelSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      <div className="h-4 w-3/4 rounded bg-line/60" />
      <div className="h-4 w-1/2 rounded bg-line/40" />
      <div className="h-4 w-2/3 rounded bg-line/40" />
    </div>
  );
}

export function PaymentDetailPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const {
    payment,
    events,
    logs,
    isPaymentPending,
    isEventsPending,
    isLogsPending,
    notFound,
    paymentError,
    eventsError,
    logsError,
  } = usePaymentDetail(paymentId);

  if (!paymentId) {
    return (
      <p className="text-sm text-danger">Missing payment ID in the URL.</p>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/"
          className="text-sm font-medium text-accent no-underline hover:underline"
        >
          ← Back to payments
        </Link>
      </div>

      {isPaymentPending && (
        <div className="animate-pulse space-y-4">
          <div className="h-10 w-48 rounded-lg bg-line/60" />
          <div className="h-24 rounded-3xl bg-line/40" />
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

      {!isPaymentPending && paymentError && !notFound && !payment && (
        <p className="text-sm text-danger">
          Could not load payment. {errorMessage(paymentError)}
        </p>
      )}

      {payment && (
        <>
          <header className="space-y-4">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold tracking-[0.16em] text-muted uppercase">
                  Payment
                </p>
                <h1 className="font-mono text-3xl font-medium tracking-tight sm:text-4xl">
                  {payment.id}
                </h1>
              </div>
              <PaymentStatusBadge status={payment.status} />
            </div>

            <div className="flex flex-wrap gap-x-8 gap-y-3 text-sm">
              <div>
                <p className="text-xs text-muted">Amount</p>
                <p className="text-2xl font-medium tabular-nums">
                  {formatAmount(payment.amount, payment.currency)}
                </p>
              </div>
              <div>
                <p className="text-xs text-muted">Gateway</p>
                <p className="font-medium">{payment.gateway}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Error code</p>
                <p className="font-mono text-copper">{payment.error_code ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Customer</p>
                <p className="font-mono text-[13px]">{payment.customer_id}</p>
              </div>
              <div>
                <p className="text-xs text-muted">Method</p>
                <p>{payment.payment_method}</p>
              </div>
            </div>
          </header>

          <div className="grid gap-6 lg:grid-cols-2">
            <DetailPanel
              title="Payment timeline"
              footer={
                eventsError ? (
                  <p className="mt-4 text-sm text-danger">
                    Could not load timeline data. {errorMessage(eventsError)}
                  </p>
                ) : undefined
              }
            >
              {isEventsPending ? <PanelSkeleton /> : <PaymentTimeline events={events} />}
            </DetailPanel>

            <div className="space-y-6">
              <DetailPanel
                title="Events"
                footer={
                  eventsError ? (
                    <p className="mt-4 text-sm text-danger">
                      Could not load events. {errorMessage(eventsError)}
                    </p>
                  ) : undefined
                }
              >
                {isEventsPending ? <PanelSkeleton /> : <PaymentEventsList events={events} />}
              </DetailPanel>
              <DetailPanel
                title="Logs"
                footer={
                  logsError ? (
                    <p className="mt-4 text-sm text-danger">
                      Could not load logs. {errorMessage(logsError)}
                    </p>
                  ) : undefined
                }
              >
                {isLogsPending ? <PanelSkeleton /> : <PaymentLogsList logs={logs} />}
              </DetailPanel>
            </div>
          </div>

          <div className="border-t border-line pt-6">
            <InvestigateButton paymentId={payment.id} />
          </div>
        </>
      )}
    </div>
  );
}
