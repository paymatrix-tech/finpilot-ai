import { Link } from "react-router-dom";

type InvestigateButtonProps = {
  paymentId: string;
};

export function InvestigateButton({ paymentId }: InvestigateButtonProps) {
  return (
    <Link
      to={`/payments/${encodeURIComponent(paymentId)}/investigate`}
      className="inline-flex items-center justify-center rounded-full bg-accent px-6 py-3 text-sm font-semibold text-panel no-underline shadow-[0_12px_30px_rgba(15,92,86,0.25)] transition hover:bg-[#0c4a45] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
    >
      Investigate with FinPilot
    </Link>
  );
}
