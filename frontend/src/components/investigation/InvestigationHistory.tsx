import { Link } from "react-router-dom";
import type { SavedInvestigation } from "../../types/investigation";
import { formatDateTime } from "../../lib/format";
import { ListEmptyHint } from "../ui/ListEmptyHint";
import { PanelSkeleton } from "../ui/PanelSkeleton";
import { QueryErrorAlert } from "../ui/QueryErrorAlert";
import { panelClass, panelPaddingClass } from "../ui/classes";
import { ConfidenceBadge } from "./ConfidenceBadge";

type InvestigationHistoryProps = {
  paymentId: string;
  items: SavedInvestigation[];
  isLoading?: boolean;
  isError?: boolean;
  error?: unknown;
  activeInvestigationId?: number;
};

export function InvestigationHistory({
  paymentId,
  items,
  isLoading = false,
  isError = false,
  error,
  activeInvestigationId,
}: InvestigationHistoryProps) {
  const basePath = `/payments/${encodeURIComponent(paymentId)}/investigations`;

  return (
    <section
      className={`${panelClass} ${panelPaddingClass}`}
      aria-labelledby="investigation-history-heading"
    >
      <h2 id="investigation-history-heading" className="text-sm font-semibold tracking-wide text-ink">
        Previous investigations
      </h2>
      <p className="mt-1 text-sm text-muted">
        Saved results for this payment. New runs are added automatically.
      </p>

      {isLoading && (
        <div className="mt-4">
          <PanelSkeleton lines={2} />
        </div>
      )}

      {isError && !isLoading && (
        <div className="mt-4">
          <QueryErrorAlert error={error} />
        </div>
      )}

      {!isLoading && !isError && items.length === 0 && (
        <div className="mt-4">
          <ListEmptyHint>
            No saved investigations yet. Run FinPilot once to build history for this payment.
          </ListEmptyHint>
        </div>
      )}

      {!isLoading && !isError && items.length > 0 && (
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
