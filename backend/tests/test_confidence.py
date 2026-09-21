"""
Unit tests for the confidence-scoring algorithm — the piece of business
logic most worth pinning down with tests since every other feature (verdict
labels, dashboard stats, PDF reports) depends on it being correct.

Run with: pytest backend/tests
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from ai.forensics.analyzer import Finding
from ai.utils.confidence import compute_confidence


def _clean_findings():
    return [
        Finding("A", "Check A", detected=False, severity="low", detail="ok", score_impact=3.0),
        Finding("B", "Check B", detected=False, severity="low", detail="ok", score_impact=2.0),
    ]


def _dirty_findings():
    return [
        Finding("A", "Check A", detected=True, severity="high", detail="bad", score_impact=-25.0),
        Finding("B", "Check B", detected=True, severity="high", detail="bad", score_impact=-20.0),
        Finding("C", "Check C", detected=True, severity="medium", detail="bad", score_impact=-15.0),
    ]


def test_clean_image_scores_as_genuine():
    result = compute_confidence(_clean_findings(), genuine_threshold=75, suspicious_threshold=45)
    assert result.verdict == "Likely Genuine"
    assert result.is_suspicious is False
    assert 0 <= result.score <= 100


def test_heavily_flagged_image_scores_as_suspicious():
    result = compute_confidence(_dirty_findings(), genuine_threshold=75, suspicious_threshold=45)
    assert result.verdict == "Highly Suspicious"
    assert result.is_suspicious is True


def test_score_is_clamped_between_0_and_100():
    huge_negative = [Finding("X", "X", True, "high", "x", -1000.0)]
    result = compute_confidence(huge_negative, genuine_threshold=75, suspicious_threshold=45)
    assert result.score == 0.0

    huge_positive = [Finding("Y", "Y", False, "low", "y", 1000.0)]
    result2 = compute_confidence(huge_positive, genuine_threshold=75, suspicious_threshold=45)
    assert result2.score == 100.0
