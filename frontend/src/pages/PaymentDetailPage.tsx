import { useParams } from "react-router-dom";
import { InvestigateButton } from "../components/payments/InvestigateButton";
import { PaymentEventsList } from "../components/payments/PaymentEventsList";
import { PaymentLogsList } from "../components/payments/PaymentLogsList";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { PaymentTimeline } from "../components/payments/PaymentTimeline";
import { BackLink } from "../components/ui/BackLink";
import { EmptyState } from "../components/ui/EmptyState";
import { PageHeader } from "../components/ui/PageHeader";
import { Panel } from "../components/ui/Panel";
import { PanelSkeleton } from "../components/ui/PanelSkeleton";
import { QueryErrorAlert } from "../components/ui/QueryErrorAlert";
import { pageStackClass } from "../components/ui/classes";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { formatAmount } from "../lib/format";

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
      <EmptyState
        title="Missing payment ID"
        description="Open a payment from the ledger to view its details."
        action={<BackLink to="/">← Back to payments</BackLink>}
      />
    );
  }

  return (
    <div className={pageStackClass}>
      <BackLink to="/">← Back to payments</BackLink>

      {isPaymentPending && (
        <div className="animate-pulse space-y-4" aria-busy="true" aria-label="Loading payment">
          <div className="h-10 w-48 rounded-lg bg-line/60" />
          <div className="h-28 rounded-3xl bg-line/40" />
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="h-48 rounded-3xl bg-line/30" />
            <div className="h-48 rounded-3xl bg-line/25" />
          </div>
        </div>
      )}

      {!isPaymentPending && notFound && (
        <EmptyState
          monoHint={paymentId}
          title="Payment not found"
          description="This ID is not in the ledger. Check the ID or search for a similar payment."
          action={<BackLink to="/">Search the ledger</BackLink>}
        />
      )}

      {!isPaymentPending && paymentError && !notFound && !payment && (
        <QueryErrorAlert error={paymentError} />
      )}

      {payment && (
        <>
          <header className="space-y-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <PageHeader
                eyebrow="Payment"
                title={<span className="font-mono text-3xl sm:text-4xl">{payment.id}</span>}
              />
              <PaymentStatusBadge status={payment.status} />
            </div>

            <dl className="flex flex-wrap gap-x-10 gap-y-4 text-sm">
              <div>
                <dt className="text-xs text-muted">Amount</dt>
                <dd className="text-2xl font-medium tabular-nums">
                  {formatAmount(payment.amount, payment.currency)}
                </dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Gateway</dt>
                <dd className="font-medium">{payment.gateway}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Error code</dt>
                <dd className="font-mono text-copper">{payment.error_code ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Customer</dt>
                <dd className="font-mono text-[13px]">{payment.customer_id}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted">Method</dt>
                <dd>{payment.payment_method}</dd>
              </div>
            </dl>
          </header>

          <div className="grid gap-6 lg:grid-cols-2">
            <Panel
              id="payment-timeline"
              title="Payment timeline"
              footer={
                eventsError ? (
                  <div className="mt-4">
                    <QueryErrorAlert error={eventsError} />
                  </div>
                ) : undefined
              }
            >
              {isEventsPending ? <PanelSkeleton /> : <PaymentTimeline events={events} />}
            </Panel>

            <div className="space-y-6">
              <Panel
                id="payment-events"
                title="Events"
                footer={
                  eventsError ? (
                    <div className="mt-4">
                      <QueryErrorAlert error={eventsError} />
                    </div>
                  ) : undefined
                }
              >
                {isEventsPending ? <PanelSkeleton /> : <PaymentEventsList events={events} />}
              </Panel>
              <Panel
                id="payment-logs"
                title="Logs"
                footer={
                  logsError ? (
                    <div className="mt-4">
                      <QueryErrorAlert error={logsError} />
                    </div>
                  ) : undefined
                }
              >
                {isLogsPending ? <PanelSkeleton /> : <PaymentLogsList logs={logs} />}
              </Panel>
            </div>
          </div>

          <div className="border-t border-line pt-8">
            <p className="mb-4 text-sm text-muted">
              FinPilot will analyze this payment, related events, logs, and internal documentation.
            </p>
            <InvestigateButton paymentId={payment.id} />
          </div>
        </>
      )}
    </div>
  );
}
