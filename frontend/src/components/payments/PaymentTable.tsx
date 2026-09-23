import { formatAmount } from "../../lib/format";
import type { Payment } from "../../types/payment";
import { PaymentStatusBadge } from "./PaymentStatusBadge";

type PaymentTableProps = {
  payments: Payment[];
};

export function PaymentTable({ payments }: PaymentTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed border-collapse text-left">
        <thead>
          <tr className="text-[11px] font-semibold tracking-[0.16em] text-muted uppercase">
            <th className="w-[20%] px-4 py-3 font-semibold sm:px-5">Payment</th>
            <th className="w-[16%] px-4 py-3 font-semibold sm:px-5">Amount</th>
            <th className="w-[18%] px-4 py-3 font-semibold sm:px-5">Status</th>
            <th className="w-[22%] px-4 py-3 font-semibold sm:px-5">Gateway</th>
            <th className="w-[24%] px-4 py-3 font-semibold sm:px-5">Error</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((payment) => (
            <tr
              key={payment.id}
              className="border-t border-line/80 transition-colors hover:bg-accent-soft/40"
            >
              <td className="px-4 py-4 sm:px-5">
                <div className="font-mono text-[13px] font-medium">{payment.id}</div>
                <div className="mt-0.5 text-xs text-muted">{payment.payment_method}</div>
              </td>
              <td className="px-4 py-4 text-[15px] font-medium tabular-nums sm:px-5">
                {formatAmount(payment.amount, payment.currency)}
              </td>
              <td className="px-4 py-4 sm:px-5">
                <PaymentStatusBadge status={payment.status} />
              </td>
              <td className="px-4 py-4 text-sm sm:px-5">{payment.gateway}</td>
              <td className="px-4 py-4 font-mono text-[12px] break-all text-copper sm:px-5">
                {payment.error_code ?? "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
