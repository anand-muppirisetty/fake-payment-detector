"""Pydantic schemas for the analysis pipeline & history endpoints."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class OCRFields(BaseModel):
    amount: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    utr: Optional[str] = None
    bank_name: Optional[str] = None
    sender_upi: Optional[str] = None
    receiver_upi: Optional[str] = None
    payment_status: Optional[str] = None
    raw_text: Optional[str] = None


class ForensicFinding(BaseModel):
    code: str            # machine-readable id, e.g. "FONT_INCONSISTENCY"
    label: str            # human label, e.g. "Font inconsistencies"
    detected: bool         # True => flagged as an anomaly
    severity: str          # "low" | "medium" | "high"
    detail: str            # short explanation of what was measured
    score_impact: float     # how many confidence points this cost (negative) or added


class ExplanationReason(BaseModel):
    text: str
    passed: bool   # True = check passed (good sign), False = check failed (bad sign)


class AnalysisOut(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    ocr: OCRFields
    forensic_findings: list[ForensicFinding]
    forensic_flags_count: int
    confidence_score: float
    verdict: str
    is_suspicious: bool
    explanation_reasons: list[ExplanationReason]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    original_filename: str
    confidence_score: float
    verdict: str
    is_suspicious: bool
    ocr_amount: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_analyses: int
    suspicious_count: int
    genuine_count: int
    needs_review_count: int
    average_confidence: float
    verdict_breakdown: dict[str, int]
    daily_timeline: list[dict[str, Any]]     # [{date: "2026-07-01", count: 3}, ...]
