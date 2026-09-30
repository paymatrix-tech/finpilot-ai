export function InsufficientEvidenceBanner() {
  return (
    <div
      className="rounded-3xl border border-copper/40 bg-page px-5 py-4 text-sm"
      role="status"
    >
      <p className="font-semibold text-copper">Insufficient evidence</p>
      <p className="mt-1 text-muted">
        FinPilot could not tie the failure to strong payment, log, and documentation signals.
        Review the payment timeline manually or rerun with a more specific question.
      </p>
    </div>
  );
}
