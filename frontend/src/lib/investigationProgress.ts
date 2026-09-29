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

export const SIMULATED_STEP_IDS = [
  "get_payment",
  "get_payment_events",
  "search_logs",
  "search_payment_docs",
  RCA_STEP_ID,
] as const;

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

export function buildSimulatedProgress(activeIndex: number): InvestigationProgressStep[] {
  return SIMULATED_STEP_IDS.map((id, index) => {
    const label = id === RCA_STEP_ID ? RCA_LABEL : toolLabel(id);
    let state: ProgressStepState = "pending";
    if (index < activeIndex) {
      state = "complete";
    } else if (index === activeIndex) {
      state = "active";
    }
    return { id: `${id}-${index}`, label, state };
  });
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
