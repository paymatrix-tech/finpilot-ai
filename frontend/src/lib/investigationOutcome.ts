export function isInsufficientEvidence(
  rootCause: string | null | undefined,
  confidence: string | null | undefined,
  evidence: string[],
): boolean {
  if (rootCause && rootCause.toLowerCase().includes("insufficient evidence")) {
    return true;
  }
  const normalized = confidence?.trim().toLowerCase();
  if (normalized === "low" && evidence.length === 0) {
    return true;
  }
  return false;
}
