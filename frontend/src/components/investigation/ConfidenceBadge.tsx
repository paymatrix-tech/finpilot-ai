type ConfidenceBadgeProps = {
  confidence: string;
};

function normalizeConfidence(value: string): "low" | "medium" | "high" {
  const normalized = value.trim().toLowerCase();
  if (normalized === "low" || normalized === "medium" || normalized === "high") {
    return normalized;
  }
  return "medium";
}

const styles: Record<"low" | "medium" | "high", { pill: string; dot: string; label: string }> =
  {
    low: {
      pill: "bg-danger-soft text-danger",
      dot: "bg-danger",
      label: "Low confidence",
    },
    medium: {
      pill: "bg-page text-copper border border-line",
      dot: "bg-copper",
      label: "Medium confidence",
    },
    high: {
      pill: "bg-success-soft text-success",
      dot: "bg-success",
      label: "High confidence",
    },
  };

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const level = normalizeConfidence(confidence);
  const style = styles[level];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold tracking-wide capitalize ${style.pill}`}
      title={style.label}
    >
      <span aria-hidden className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {level} confidence
    </span>
  );
}
