"""
Analysis model — one row per uploaded screenshot analyzed by the AI pipeline.
Stores OCR extraction, forensic findings, and the final confidence verdict.
"""
import enum
from datetime import datetime

from sqlalchemy import (
    JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class VerdictLabel(str, enum.Enum):
    LIKELY_GENUINE = "Likely Genuine"
    NEEDS_REVIEW = "Needs Manual Review"
    HIGHLY_SUSPICIOUS = "Highly Suspicious"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- File storage ---
    stored_filename = Column(String(255), nullable=False)   # UUID-based name on disk
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash_sha256 = Column(String(64), nullable=False, index=True)

    # --- OCR extracted fields ---
    ocr_amount = Column(String(50), nullable=True)
    ocr_date = Column(String(50), nullable=True)
    ocr_time = Column(String(50), nullable=True)
    ocr_utr = Column(String(50), nullable=True)
    ocr_bank_name = Column(String(120), nullable=True)
    ocr_sender_upi = Column(String(120), nullable=True)
    ocr_receiver_upi = Column(String(120), nullable=True)
    ocr_payment_status = Column(String(50), nullable=True)
    ocr_raw_text = Column(Text, nullable=True)

    # --- Forensic AI findings (structured JSON, see ai/forensics) ---
    forensic_findings = Column(JSON, nullable=True)   # list[FindingDict]
    forensic_flags_count = Column(Integer, default=0)

    # --- Confidence verdict ---
    confidence_score = Column(Float, nullable=False)   # 0-100
    verdict = Column(Enum(VerdictLabel), nullable=False)
    is_suspicious = Column(Boolean, default=False, nullable=False)

    # --- Explainability summary (human readable reasons) ---
    explanation_reasons = Column(JSON, nullable=True)   # list[{text, passed: bool}]

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    owner = relationship("User", back_populates="analyses")
