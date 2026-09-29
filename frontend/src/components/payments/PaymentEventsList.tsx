import type { PaymentEvent } from "../../types/paymentDetail";
import { formatEventType, formatTime } from "../../lib/format";
import { ListEmptyHint } from "../ui/ListEmptyHint";

type PaymentEventsListProps = {
  events: PaymentEvent[];
};

export function PaymentEventsList({ events }: PaymentEventsListProps) {
  if (events.length === 0) {
    return <ListEmptyHint>No events recorded for this payment.</ListEmptyHint>;
  }

  return (
    <ul className="divide-y divide-line/80">
      {events.map((event) => (
        <li
          key={event.id}
          className="flex flex-wrap items-baseline gap-x-3 gap-y-1 py-3 first:pt-0 last:pb-0"
        >
          <span className="font-mono text-xs text-muted tabular-nums">
            {formatTime(event.created_at)}
          </span>
          <span className="font-mono text-[13px] font-medium">{event.event_type}</span>
          <span className="text-sm text-muted">{formatEventType(event.event_type)}</span>
        </li>
      ))}
    </ul>
  );
}
