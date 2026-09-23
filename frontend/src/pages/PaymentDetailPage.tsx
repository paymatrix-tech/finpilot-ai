import { Link, useParams } from "react-router-dom";
import type { PropsWithChildren } from "react";
import { InvestigateButton } from "../components/payments/InvestigateButton";
import { PaymentEventsList } from "../components/payments/PaymentEventsList";
import { PaymentLogsList } from "../components/payments/PaymentLogsList";
import { PaymentStatusBadge } from "../components/payments/PaymentStatusBadge";
import { PaymentTimeline } from "../components/payments/PaymentTimeline";
import { usePaymentDetail } from "../hooks/usePaymentDetail";
import { formatAmount } from "../lib/format";

function DetailPanel({
  title,
  children,
}: PropsWithChildren<{ title: string }>) {
  return (
    <section className="rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_60px_rgba(28,25,21,0.04)] sm:p-6">
      <h2 className="text-sm font-semibold tracking-wide text-ink">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

export function PaymentDetailPage() {
  const { paymentId } = useParams<{ paymentId: string }>();
  const { payment, events, logs, isPending, isError, error } = usePaymentDetail(paymentId);

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

      {isPending && (
        <div className="animate-pulse space-y-4">
          <div className="h-10 w-48 rounded-lg bg-line/60" />
          <div className="h-24 rounded-3xl bg-line/40" />
        </div>
      )}

      {isError && !payment && (
        <p className="text-sm text-danger">
          Could not load payment.{" "}
          {error instanceof Error ? error.message : "Request failed"}
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
            <DetailPanel title="Payment timeline">
              <PaymentTimeline events={events} />
            </DetailPanel>

            <div className="space-y-6">
              <DetailPanel title="Events">
                <PaymentEventsList events={events} />
              </DetailPanel>
              <DetailPanel title="Logs">
                <PaymentLogsList logs={logs} />
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
