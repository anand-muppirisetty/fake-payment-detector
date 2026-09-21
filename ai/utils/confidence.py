"""
Confidence scoring algorithm.

Combines every forensic Finding's `score_impact` into a single 0-100
"genuineness confidence" score, then maps that score to a verdict label
using the configurable thresholds in app.core.config.

Design notes:
- We start from a neutral baseline of 70 (slightly optimistic — most real
  screenshots pass most checks) rather than 50, because the majority of
  forensic checks below contribute small positive nudges when they PASS
  (i.e. find nothing wrong), and larger negative nudges when they FAIL.
  This keeps a clean, unedited screenshot comfortably in "Likely Genuine"
  territory while a handful of high-severity flags can still drag a score
  down sharply — mirroring how a human reviewer would weigh a few strong
  red flags over many weak reassurances.
- The score is clamped to [0, 100].
- This is explicitly a heuristic aggregate, not a probability calibrated
  against ground truth (that requires the labeled dataset described in
  ai/models/train.py under Future Scope).
"""
from __future__ import annotations

from dataclasses import dataclass

from ai.forensics.analyzer import Finding

BASELINE_SCORE = 70.0


@dataclass
class ConfidenceResult:
    score: float
    verdict: str
    is_suspicious: bool


def compute_confidence(findings: list[Finding], genuine_threshold: int,
                        suspicious_threshold: int) -> ConfidenceResult:
    score = BASELINE_SCORE
    for f in findings:
        score += f.score_impact

    score = max(0.0, min(100.0, round(score, 1)))

    if score >= genuine_threshold:
        verdict = "Likely Genuine"
    elif score < suspicious_threshold:
        verdict = "Highly Suspicious"
    else:
        verdict = "Needs Manual Review"

    is_suspicious = verdict != "Likely Genuine"
    return ConfidenceResult(score=score, verdict=verdict, is_suspicious=is_suspicious)


def build_explanation_reasons(findings: list[Finding], ocr_utr: str | None) -> list[dict]:
    """
    Produce the human-facing explainability list shown in the UI, e.g.:
      [checkmark] Fonts inconsistent
      [x] Metadata missing
      [checkmark] UTR format valid
    `passed=True` means the check reflects positively on genuineness.
    """
    reasons: list[dict] = []
    for f in findings:
        passed = not f.detected
        reasons.append({"text": f.label, "passed": passed, "detail": f.detail})
    return reasons
