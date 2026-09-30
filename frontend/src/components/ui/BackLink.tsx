import type { ReactNode } from "react";
import { Link } from "react-router-dom";

type BackLinkProps = {
  to: string;
  children: ReactNode;
};

export function BackLink({ to, children }: BackLinkProps) {
  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1 text-sm font-medium text-accent no-underline transition hover:underline"
    >
      {children}
    </Link>
  );
}
