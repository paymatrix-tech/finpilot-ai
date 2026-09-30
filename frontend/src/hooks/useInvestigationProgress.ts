import { useMemo } from "react";
import {
  buildLiveStreamProgress,
  buildProgressFromToolSteps,
  type InvestigationProgressStep,
} from "../lib/investigationProgress";
import type { ToolExecutionStep } from "../types/investigation";

type LiveStreamState = {
  steps: ToolExecutionStep[];
  rcaPhase: boolean;
  started: boolean;
};

export function useInvestigationProgress(
  isRunning: boolean,
  toolSteps: ToolExecutionStep[] | undefined,
  liveStream?: LiveStreamState,
): { steps: InvestigationProgressStep[]; isLive: boolean } {
  const steps = useMemo(() => {
    if (isRunning && liveStream) {
      return buildLiveStreamProgress(liveStream);
    }
    if (!isRunning && toolSteps) {
      return buildProgressFromToolSteps(toolSteps);
    }
    return [];
  }, [isRunning, liveStream, toolSteps]);

  return { steps, isLive: isRunning };
}
