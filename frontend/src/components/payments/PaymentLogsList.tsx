import type { PaymentLog } from "../../types/paymentDetail";
import { formatTime } from "../../lib/format";

type PaymentLogsListProps = {
  logs: PaymentLog[];
};

const levelStyles: Record<string, string> = {
  WARN: "text-copper",
  ERROR: "text-danger",
  INFO: "text-muted",
};

export function PaymentLogsList({ logs }: PaymentLogsListProps) {
  if (logs.length === 0) {
    return <p className="text-sm text-muted">No logs recorded.</p>;
  }

  return (
    <ul className="divide-y divide-line/80">
      {logs.map((log) => (
        <li key={log.id} className="py-3 first:pt-0 last:pb-0">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <span className="font-mono text-xs text-muted tabular-nums">
              {formatTime(log.created_at)}
            </span>
            <span
              className={`font-mono text-[11px] font-semibold tracking-wide uppercase ${
                levelStyles[log.level] ?? "text-muted"
              }`}
            >
              {log.level}
            </span>
            <span className="text-sm">{log.message}</span>
          </div>
          <p className="mt-1 text-xs text-muted">{log.service}</p>
        </li>
      ))}
    </ul>
  );
}
