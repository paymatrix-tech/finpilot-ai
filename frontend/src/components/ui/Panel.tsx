import type { PropsWithChildren, ReactNode } from "react";
import { panelClass, panelPaddingClass } from "./classes";

type PanelProps = PropsWithChildren<{
  title?: string;
  description?: string;
  footer?: ReactNode;
  id?: string;
  className?: string;
}>;

export function Panel({ title, description, footer, id, className = "", children }: PanelProps) {
  return (
    <section className={`${panelClass} ${panelPaddingClass} ${className}`} aria-labelledby={id}>
      {(title || description) && (
        <div className="mb-4">
          {title && (
            <h2 id={id} className="text-sm font-semibold tracking-wide text-ink">
              {title}
            </h2>
          )}
          {description && <p className="mt-1 text-sm text-muted">{description}</p>}
        </div>
      )}
      {children}
      {footer}
    </section>
  );
}
