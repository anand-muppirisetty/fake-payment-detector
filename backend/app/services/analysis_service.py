"""
Orchestrates the end-to-end analysis pipeline:
  1. OCR extraction (ai/ocr)
  2. Forensic analysis (ai/forensics + ai/models CNN signal)
  3. Confidence scoring (ai/utils/confidence)
  4. Persists everything to the `analyses` table
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from ai.forensics.analyzer import run_forensic_analysis, findings_to_dicts
from ai.ocr.extractor import run_ocr
from ai.utils.confidence import build_explanation_reasons, compute_confidence
from app.core.config import settings
from app.models.analysis import Analysis, VerdictLabel


def run_full_analysis(db: Session, owner_id: int, stored_filename: str, original_filename: str,
                       file_size_bytes: int, file_hash: str, abs_path: str, image_bytes: bytes) -> Analysis:
    ocr_result = run_ocr(abs_path)

    findings = run_forensic_analysis(
        image_path=abs_path,
        image_bytes=image_bytes,
        ocr_amount=ocr_result.amount,
        ocr_utr=ocr_result.utr,
    )

    confidence = compute_confidence(
        findings,
        genuine_threshold=settings.CONFIDENCE_GENUINE_THRESHOLD,
        suspicious_threshold=settings.CONFIDENCE_SUSPICIOUS_THRESHOLD,
    )
    reasons = build_explanation_reasons(findings, ocr_result.utr)
    flags_count = sum(1 for f in findings if f.detected)

    verdict_enum = {
        "Likely Genuine": VerdictLabel.LIKELY_GENUINE,
        "Needs Manual Review": VerdictLabel.NEEDS_REVIEW,
        "Highly Suspicious": VerdictLabel.HIGHLY_SUSPICIOUS,
    }[confidence.verdict]

    analysis = Analysis(
        owner_id=owner_id,
        stored_filename=stored_filename,
        original_filename=original_filename,
        file_size_bytes=file_size_bytes,
        file_hash_sha256=file_hash,
        ocr_amount=ocr_result.amount,
        ocr_date=ocr_result.date,
        ocr_time=ocr_result.time,
        ocr_utr=ocr_result.utr,
        ocr_bank_name=ocr_result.bank_name,
        ocr_sender_upi=ocr_result.sender_upi,
        ocr_receiver_upi=ocr_result.receiver_upi,
        ocr_payment_status=ocr_result.payment_status,
        ocr_raw_text=ocr_result.raw_text,
        forensic_findings=findings_to_dicts(findings),
        forensic_flags_count=flags_count,
        confidence_score=confidence.score,
        verdict=verdict_enum,
        is_suspicious=confidence.is_suspicious,
        explanation_reasons=reasons,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis
