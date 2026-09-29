export type ToolExecutionStep = {
  tool: string;
  arguments: Record<string, unknown>;
  result: unknown;
};

export type InvestigationResult = {
  payment_id: string;
  question: string;
  root_cause: string;
  confidence: string;
  evidence: string[];
  recommendation: string;
  sources: string[];
  answer: string;
  steps: ToolExecutionStep[];
  model: string;
  provider: string;
};

export type CreateInvestigationRequest = {
  payment_id: string;
  question?: string;
};
