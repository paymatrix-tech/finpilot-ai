import { ConfidenceBadge } from "./ConfidenceBadge";

export type InvestigationResultsData = {
  question: string;
  root_cause: string;
  confidence: string;
  evidence: string[];
  recommendation: string;
  sources?: string[];
  model?: string;
  provider?: string;
};

type InvestigationResultsProps = {
  data: InvestigationResultsData;
};

export function InvestigationResults({ data }: InvestigationResultsProps) {
  const evidenceItems = data.evidence.map((item) =>
    typeof item === "string" ? item : String(item),
  );

  return (
    <div className="space-y-6">
      <section
        className="rounded-3xl border border-accent/25 bg-accent-soft/40 p-5 sm:p-6"
        aria-labelledby="root-cause-heading"
      >
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h2 id="root-cause-heading" className="text-sm font-semibold tracking-wide text-ink">
            Root cause
          </h2>
          <ConfidenceBadge confidence={data.confidence} />
        </div>
        <p className="mt-3 text-lg font-medium leading-relaxed text-ink">{data.root_cause}</p>
      </section>

      <section
        className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
        aria-labelledby="question-heading"
      >
        <h2 id="question-heading" className="text-sm font-semibold tracking-wide text-ink">
          Question
        </h2>
        <p className="mt-3 text-base text-ink">{data.question}</p>
      </section>

      <section
        className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
        aria-labelledby="evidence-heading"
      >
        <h2 id="evidence-heading" className="text-sm font-semibold tracking-wide text-ink">
          Evidence
        </h2>
        {evidenceItems.length === 0 ? (
          <p className="mt-3 text-sm text-muted">No evidence items were returned.</p>
        ) : (
          <ul className="mt-4 list-none space-y-2 p-0">
            {evidenceItems.map((item, index) => (
              <li
                key={`${index}-${item.slice(0, 24)}`}
                className="flex gap-3 text-sm leading-relaxed text-ink"
              >
                <span
                  aria-hidden
                  className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        )}
        {data.sources && data.sources.length > 0 && (
          <div className="mt-5 border-t border-line pt-4">
            <p className="text-xs font-semibold tracking-wide text-muted uppercase">
              Documentation sources
            </p>
            <ul className="mt-2 flex flex-wrap gap-2">
              {data.sources.map((source) => (
                <li
                  key={source}
                  className="rounded-full bg-page px-3 py-1 font-mono text-xs text-muted"
                >
                  {source}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section
        className="rounded-3xl border border-line bg-panel p-5 sm:p-6"
        aria-labelledby="recommendation-heading"
      >
        <h2
          id="recommendation-heading"
          className="text-sm font-semibold tracking-wide text-ink"
        >
          Recommendation
        </h2>
        <p className="mt-3 text-base leading-relaxed text-ink">{data.recommendation}</p>
      </section>

      {data.model && data.provider && (
        <p className="text-center text-xs text-muted">
          Model {data.model} ({data.provider})
        </p>
      )}
    </div>
  );
}
