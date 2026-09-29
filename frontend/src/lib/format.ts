const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

export function formatAmount(amount: string, code: string): string {
  const value = Number(amount);
  if (Number.isNaN(value) || code !== "USD") {
    return `${amount} ${code}`;
  }
  return currency.format(value);
}

const timeFormatter = new Intl.DateTimeFormat("en-US", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const dateTimeFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export function formatDateTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return dateTimeFormatter.format(date);
}

export function formatTime(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return timeFormatter.format(date);
}

const EVENT_LABELS: Record<string, string> = {
  PAYMENT_CREATED: "Created",
  VALIDATED: "Validated",
  GATEWAY_REQUEST: "Gateway request",
  GATEWAY_RESPONSE: "Gateway response",
  PAYMENT_FAILED: "Payment failed",
  PAYMENT_SUCCEEDED: "Payment succeeded",
};

export function formatEventType(eventType: string): string {
  return EVENT_LABELS[eventType] ?? eventType.replaceAll("_", " ").toLowerCase();
}

export function formatEventDetail(
  eventType: string,
  metadata: Record<string, unknown>,
): string | null {
  if (eventType === "GATEWAY_RESPONSE") {
    const errorCode = metadata.error_code;
    if (typeof errorCode === "string" && errorCode.length > 0) {
      return errorCode;
    }
    const result = metadata.result;
    if (typeof result === "string" && result.length > 0) {
      return result;
    }
  }
  return null;
}
