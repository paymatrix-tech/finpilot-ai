import { Link, useParams } from "react-router-dom";

export function InvestigatePlaceholderPage() {
  const { paymentId } = useParams<{ paymentId: string }>();

  return (
    <div className="mx-auto max-w-lg space-y-4 text-center">
      <h1 className="font-display text-3xl">Investigation</h1>
      <p className="text-muted">
        FinPilot AI investigation for{" "}
        <span className="font-mono text-ink">{paymentId}</span> is planned for Week 2.
      </p>
      {paymentId && (
        <Link
          to={`/payments/${encodeURIComponent(paymentId)}`}
          className="inline-block text-sm font-medium text-accent no-underline hover:underline"
        >
          ← Back to payment details
        </Link>
      )}
    </div>
  );
}
