type PaymentStatusBadgeProps = {
  status: string;
};

export function PaymentStatusBadge({ status }: PaymentStatusBadgeProps) {
  const isFailed = status.toLowerCase() === "failed";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide ${
        isFailed ? "bg-danger-soft text-danger" : "bg-success-soft text-success"
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${isFailed ? "bg-danger" : "bg-success"}`}
      />
      {status}
    </span>
  );
}
