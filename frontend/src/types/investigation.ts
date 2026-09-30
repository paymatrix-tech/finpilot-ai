export type ToolExecutionStep = {
  tool: string;
  arguments: Record<string, unknown>;
  result: unknown;
};

export type SavedInvestigation = {
  id: number;
  payment_id: string;
  question: string;
  root_cause: string | null;
  evidence: string[];
  recommendation: string | null;
  confidence: string | null;
  created_at: string;
};

export type InvestigationListResponse = {
  items: SavedInvestigation[];
};

export type InvestigationResult = {
  id: number | null;
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
  insufficient_evidence: boolean;
};

export type CreateInvestigationRequest = {
  payment_id: string;
  question?: string;
};
