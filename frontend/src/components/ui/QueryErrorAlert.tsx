import type { ReactNode } from "react";
import { presentApiError } from "../../lib/apiErrors";
import { panelClass, panelPaddingClass } from "./classes";

type QueryErrorAlertProps = {
  error: unknown;
  footer?: ReactNode;
};

export function QueryErrorAlert({ error, footer }: QueryErrorAlertProps) {
  const { title, message, suggestion } = presentApiError(error);

  return (
    <div
      className={`${panelClass} ${panelPaddingClass} border-danger/25 bg-danger-soft/40`}
      role="alert"
    >
      <p className="font-semibold text-ink">{title}</p>
      <p className="mt-1 text-sm text-danger">{message}</p>
      {suggestion && <p className="mt-2 text-sm text-muted">{suggestion}</p>}
      {footer && <div className="mt-4">{footer}</div>}
    </div>
  );
}
