import { useEffect, useMemo, useState } from "react";
import {
  buildProgressFromToolSteps,
  buildSimulatedProgress,
  type InvestigationProgressStep,
  SIMULATED_STEP_IDS,
} from "../lib/investigationProgress";
import type { ToolExecutionStep } from "../types/investigation";

const STEP_INTERVAL_MS = 1100;

export function useInvestigationProgress(
  isRunning: boolean,
  toolSteps: ToolExecutionStep[] | undefined,
): { steps: InvestigationProgressStep[]; isLive: boolean } {
  const [simulatedIndex, setSimulatedIndex] = useState(0);

  useEffect(() => {
    if (!isRunning) {
      setSimulatedIndex(0);
      return;
    }

    setSimulatedIndex(0);
    const interval = window.setInterval(() => {
      setSimulatedIndex((previous) =>
        Math.min(previous + 1, SIMULATED_STEP_IDS.length - 1),
      );
    }, STEP_INTERVAL_MS);

    return () => window.clearInterval(interval);
  }, [isRunning]);

  const steps = useMemo(() => {
    if (isRunning) {
      return buildSimulatedProgress(simulatedIndex);
    }
    if (toolSteps && toolSteps.length >= 0) {
      return buildProgressFromToolSteps(toolSteps);
    }
    return [];
  }, [isRunning, simulatedIndex, toolSteps]);

  return { steps, isLive: isRunning };
}
