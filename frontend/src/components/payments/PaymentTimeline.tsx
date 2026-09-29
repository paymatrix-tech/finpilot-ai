import type { PaymentEvent } from "../../types/paymentDetail";
import { formatEventDetail, formatEventType } from "../../lib/format";
import { ListEmptyHint } from "../ui/ListEmptyHint";

type PaymentTimelineProps = {
  events: PaymentEvent[];
};

export function PaymentTimeline({ events }: PaymentTimelineProps) {
  if (events.length === 0) {
    return <ListEmptyHint>No timeline events recorded for this payment.</ListEmptyHint>;
  }

  return (
    <ol className="relative space-y-0">
      {events.map((event, index) => {
        const detail = formatEventDetail(event.event_type, event.metadata);
        const isLast = index === events.length - 1;
        const isFailure =
          event.event_type === "PAYMENT_FAILED" ||
          (event.event_type === "GATEWAY_RESPONSE" && event.status === "DECLINED");

        return (
          <li key={event.id} className="relative flex gap-4 pb-6 last:pb-0">
            {!isLast && (
              <span
                aria-hidden
                className="absolute top-3 left-[7px] h-[calc(100%-4px)] w-px bg-line"
              />
            )}
            <span
              className={`relative z-10 mt-1.5 h-3.5 w-3.5 shrink-0 rounded-full border-2 ${
                isFailure
                  ? "border-danger bg-danger-soft"
                  : "border-accent bg-accent-soft"
              }`}
            />
            <div className="min-w-0 pt-0.5">
              <p className="text-sm font-medium">{formatEventType(event.event_type)}</p>
              {detail && (
                <p className="mt-0.5 font-mono text-xs text-copper">{detail}</p>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
