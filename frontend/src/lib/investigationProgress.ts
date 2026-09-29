import type { ToolExecutionStep } from "../types/investigation";

export type ProgressStepState = "pending" | "active" | "complete" | "error";

export type InvestigationProgressStep = {
  id: string;
  label: string;
  detail?: string;
  state: ProgressStepState;
};

const TOOL_LABELS: Record<string, string> = {
  get_payment: "Payment retrieved",
  get_payment_events: "Events retrieved",
  search_logs: "Logs searched",
  search_payment_docs: "Documentation searched",
};

const RCA_STEP_ID = "generate_rca";
const RCA_LABEL = "Generating RCA";
const GATHERING_LABEL = "Gathering evidence with tools";

function toolLabel(toolName: string): string {
  return TOOL_LABELS[toolName] ?? toolName.replaceAll("_", " ");
}

function stepDetail(step: ToolExecutionStep): string | undefined {
  const args = step.arguments;
  if (typeof args.query === "string" && args.query.trim()) {
    return `query: "${args.query.trim()}"`;
  }
  if (typeof args.payment_id === "string") {
    return args.payment_id;
  }
  return undefined;
}

function isStepError(result: unknown): boolean {
  return (
    typeof result === "object" &&
    result !== null &&
    "error" in result &&
    typeof (result as { error?: unknown }).error === "string"
  );
}

export function buildLiveStreamProgress(live: {
  steps: ToolExecutionStep[];
  rcaPhase: boolean;
  started: boolean;
}): InvestigationProgressStep[] {
  const rows: InvestigationProgressStep[] = live.steps.map((step, index) => {
    const errored = isStepError(step.result);
    return {
      id: `${step.tool}-${index}`,
      label: toolLabel(step.tool),
      detail: stepDetail(step),
      state: errored ? "error" : "complete",
    };
  });

  if (live.rcaPhase) {
    rows.push({
      id: `${RCA_STEP_ID}-active`,
      label: RCA_LABEL,
      state: "active",
    });
    return rows;
  }

  if (live.started) {
    rows.push({
      id: "gathering-active",
      label: GATHERING_LABEL,
      state: "active",
    });
  }

  return rows;
}

export function buildProgressFromToolSteps(
  toolSteps: ToolExecutionStep[],
): InvestigationProgressStep[] {
  const mapped = toolSteps.map((step, index) => {
    const errored = isStepError(step.result);
    return {
      id: `${step.tool}-${index}`,
      label: toolLabel(step.tool),
      detail: stepDetail(step),
      state: errored ? "error" : "complete",
    } satisfies InvestigationProgressStep;
  });

  mapped.push({
    id: RCA_STEP_ID,
    label: "Root cause analysis complete",
    detail: undefined,
    state: "complete",
  });

  return mapped;
}
