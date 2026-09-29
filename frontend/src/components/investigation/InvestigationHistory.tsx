import { Link } from "react-router-dom";
import type { SavedInvestigation } from "../../types/investigation";
import { formatDateTime } from "../../lib/format";
import { ConfidenceBadge } from "./ConfidenceBadge";

type InvestigationHistoryProps = {
  paymentId: string;
  items: SavedInvestigation[];
  isLoading?: boolean;
  activeInvestigationId?: number;
};

export function InvestigationHistory({
  paymentId,
  items,
  isLoading = false,
  activeInvestigationId,
}: InvestigationHistoryProps) {
  const basePath = `/payments/${encodeURIComponent(paymentId)}/investigations`;

  return (
    <section
      className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
      aria-labelledby="investigation-history-heading"
    >
      <h2 id="investigation-history-heading" className="text-sm font-semibold tracking-wide text-ink">
        Previous investigations
      </h2>
      <p className="mt-1 text-sm text-muted">
        Saved results for this payment. New runs are added automatically.
      </p>

      {isLoading && (
        <div className="mt-4 animate-pulse space-y-3">
          <div className="h-14 rounded-2xl bg-line/40" />
          <div className="h-14 rounded-2xl bg-line/30" />
        </div>
      )}

      {!isLoading && items.length === 0 && (
        <p className="mt-4 text-sm text-muted">No saved investigations yet for this payment.</p>
      )}

      {!isLoading && items.length > 0 && (
        <ul className="mt-4 list-none space-y-2 p-0">
          {items.map((item) => {
            const isActive = activeInvestigationId === item.id;
            return (
              <li key={item.id}>
                <Link
                  to={`${basePath}/${item.id}`}
                  className={`block rounded-2xl border px-4 py-3 no-underline transition ${
                    isActive
                      ? "border-accent bg-accent-soft/50"
                      : "border-line bg-page hover:border-accent/40"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="text-sm font-medium text-ink">
                      {item.root_cause ?? "Investigation"}
                    </p>
                    {item.confidence && <ConfidenceBadge confidence={item.confidence} />}
                  </div>
                  <p className="mt-1 line-clamp-2 text-sm text-muted">{item.question}</p>
                  <p className="mt-2 font-mono text-xs text-muted">
                    {formatDateTime(item.created_at)}
                  </p>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
