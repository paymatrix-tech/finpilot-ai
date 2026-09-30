import type { ReactNode } from "react";
import { panelClass, panelPaddingClass } from "./classes";

type EmptyStateProps = {
  title: string;
  description?: string;
  action?: ReactNode;
  monoHint?: string;
  compact?: boolean;
};

export function EmptyState({
  title,
  description,
  action,
  monoHint,
  compact = false,
}: EmptyStateProps) {
  return (
    <div
      className={`${panelClass} ${compact ? "px-5 py-8" : panelPaddingClass} text-center`}
      role="status"
    >
      {monoHint && <p className="font-mono text-base text-ink sm:text-lg">{monoHint}</p>}
      <p className={`font-medium text-ink ${monoHint ? "mt-2" : ""}`}>{title}</p>
      {description && (
        <p className="mx-auto mt-2 max-w-sm text-sm leading-relaxed text-muted">{description}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
