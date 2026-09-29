import type { InvestigationProgressStep } from "../../lib/investigationProgress";

type InvestigationProgressProps = {
  steps: InvestigationProgressStep[];
  isLive?: boolean;
};

function StepIcon({ state }: { state: InvestigationProgressStep["state"] }) {
  if (state === "complete") {
    return (
      <span
        aria-hidden
        className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-success-soft text-xs font-bold text-success"
      >
        ✓
      </span>
    );
  }
  if (state === "error") {
    return (
      <span
        aria-hidden
        className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-danger-soft text-xs font-bold text-danger"
      >
        !
      </span>
    );
  }
  if (state === "active") {
    return (
      <span
        aria-hidden
        className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent-soft text-sm font-bold text-accent motion-safe:animate-pulse"
      >
        →
      </span>
    );
  }
  return (
    <span
      aria-hidden
      className="grid h-6 w-6 shrink-0 place-items-center rounded-full border border-line bg-page text-[10px] text-muted"
    >
      ○
    </span>
  );
}

export function InvestigationProgress({ steps, isLive = false }: InvestigationProgressProps) {
  if (steps.length === 0) {
    return null;
  }

  return (
    <section
      className="rounded-3xl border border-line bg-panel p-5 shadow-[0_24px_60px_rgba(28,25,21,0.04)] sm:p-6"
      aria-labelledby="investigation-progress-heading"
      aria-busy={isLive}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 id="investigation-progress-heading" className="text-sm font-semibold tracking-wide text-ink">
          Investigation progress
        </h2>
        {isLive && (
          <span className="text-xs font-medium tracking-wide text-accent uppercase">
            In progress
          </span>
        )}
      </div>

      <ol
        className="mt-4 list-none space-y-0 p-0"
        aria-live={isLive ? "polite" : "off"}
        aria-relevant="additions text"
      >
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1;
          const rowMuted = step.state === "pending";

          return (
            <li key={step.id} className="flex gap-3">
              <div className="flex flex-col items-center">
                <StepIcon state={step.state} />
                {!isLast && (
                  <span
                    aria-hidden
                    className={`my-1 w-px flex-1 min-h-4 ${
                      step.state === "complete" ? "bg-success/40" : "bg-line"
                    }`}
                  />
                )}
              </div>
              <div className={`pb-4 ${isLast ? "pb-0" : ""}`}>
                <p
                  className={`text-sm font-medium ${
                    rowMuted ? "text-muted" : "text-ink"
                  } ${step.state === "active" ? "text-accent" : ""}`}
                >
                  {step.label}
                </p>
                {step.detail && (
                  <p className="mt-0.5 font-mono text-xs text-muted">{step.detail}</p>
                )}
                {step.state === "error" && (
                  <p className="mt-0.5 text-xs text-danger">Tool returned an error</p>
                )}
              </div>
            </li>
          );
        })}
      </ol>

      {isLive && (
        <p className="mt-2 border-t border-line pt-4 text-sm text-muted">
          FinPilot is calling tools and building evidence. Results will appear below when ready.
        </p>
      )}
    </section>
  );
}
