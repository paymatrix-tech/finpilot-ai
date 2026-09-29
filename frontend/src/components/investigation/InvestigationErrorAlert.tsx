import type { ReactNode } from "react";
import { presentApiError } from "../../lib/apiErrors";

type InvestigationErrorAlertProps = {
  error: unknown;
  footer?: ReactNode;
};

export function InvestigationErrorAlert({ error, footer }: InvestigationErrorAlertProps) {
  const { title, message, suggestion } = presentApiError(error);

  return (
    <div
      className="rounded-3xl border border-danger/30 bg-danger-soft px-5 py-4 text-sm text-danger"
      role="alert"
    >
      <p className="font-semibold text-ink">{title}</p>
      <p className="mt-1 text-danger">{message}</p>
      {suggestion && <p className="mt-2 text-muted">{suggestion}</p>}
      {footer && <div className="mt-3">{footer}</div>}
    </div>
  );
}
