"""
OCR extraction module.

Uses EasyOCR (falls back to Tesseract if EasyOCR/torch is unavailable in the
runtime environment) to pull raw text out of a UPI payment screenshot, then
applies regex/rule-based parsing to pull out structured fields:
amount, date, time, UTR/reference number, bank name, sender UPI id,
receiver UPI id and payment status.

This module purely reads what is printed in the image. It has no way to
confirm the transaction actually happened at a bank — see forensics/ and
docs/README.md for the scope disclaimer.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# --- Lazy, optional import of EasyOCR so the module still imports (e.g. for
# unit tests / docs generation) in environments where the heavy CV/torch
# stack isn't installed. Falls back to pytesseract if present. ---
_easyocr_reader = None
_backend = None


def _get_reader():
    global _easyocr_reader, _backend
    if _easyocr_reader is not None or _backend is not None:
        return _easyocr_reader, _backend
    try:
        import easyocr  # noqa: WPS433 (intentional lazy import)
        _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        _backend = "easyocr"
        logger.info("OCR backend: EasyOCR")
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("EasyOCR unavailable (%s); falling back to Tesseract", exc)
        _easyocr_reader = None
        _backend = "tesseract"
    return _easyocr_reader, _backend


@dataclass
class OCRResult:
    raw_text: str
    amount: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    utr: Optional[str] = None
    bank_name: Optional[str] = None
    sender_upi: Optional[str] = None
    receiver_upi: Optional[str] = None
    payment_status: Optional[str] = None
    line_boxes: list[dict] = field(default_factory=list)  # bbox + text + confidence


# --- Regex patterns tuned for common UPI app screenshot layouts
# (GPay, PhonePe, Paytm, BHIM, bank apps) ---
AMOUNT_RE = re.compile(r"(?:₹|Rs\.?|INR)\s?([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]{1,2})?)", re.IGNORECASE)
UTR_RE = re.compile(r"\b(?:UTR|UPI\s?Ref(?:erence)?(?:\s?No)?|Txn\s?ID|Ref\s?No\.?)\D{0,5}([A-Z0-9]{9,22})\b", re.IGNORECASE)
UPI_ID_RE = re.compile(r"\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b")
DATE_RE = re.compile(r"\b(\d{1,2}[\s\-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s\-/]\d{2,4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b", re.IGNORECASE)
TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM|am|pm)?)\b")
STATUS_KEYWORDS = {
    "success": ["success", "successful", "completed", "paid"],
    "failed": ["failed", "declined", "unsuccessful"],
    "pending": ["pending", "processing", "in progress"],
}
KNOWN_BANKS = [
    "State Bank of India", "SBI", "HDFC Bank", "HDFC", "ICICI Bank", "ICICI",
    "Axis Bank", "Kotak Mahindra", "Kotak", "Punjab National Bank", "PNB",
    "Bank of Baroda", "Canara Bank", "Union Bank", "IndusInd Bank", "Yes Bank",
    "IDFC FIRST Bank", "IDBI Bank", "Bank of India", "Central Bank of India",
    "Paytm Payments Bank", "Federal Bank",
]


def _extract_field(pattern: re.Pattern, text: str) -> Optional[str]:
    m = pattern.search(text)
    return m.group(1).strip() if m else None


def _extract_status(text: str) -> Optional[str]:
    lowered = text.lower()
    for status, keywords in STATUS_KEYWORDS.items():
        if any(k in lowered for k in keywords):
            return status.capitalize()
    return None


def _extract_bank(text: str) -> Optional[str]:
    for bank in KNOWN_BANKS:
        if bank.lower() in text.lower():
            return bank
    return None


def _extract_upi_ids(text: str) -> tuple[Optional[str], Optional[str]]:
    """
    Best-effort heuristic: the first UPI-style id found is treated as sender,
    the second distinct one as receiver. Screenshot layouts vary widely, so
    downstream UI should let a human confirm/correct these.
    """
    ids = UPI_ID_RE.findall(text)
    # de-duplicate while preserving order
    seen: list[str] = []
    for i in ids:
        if i not in seen:
            seen.append(i)
    sender = seen[0] if len(seen) >= 1 else None
    receiver = seen[1] if len(seen) >= 2 else None
    return sender, receiver


def run_ocr(image_path: str) -> OCRResult:
    """
    Run OCR on the image at `image_path` and parse structured fields.
    Returns an OCRResult; fields that could not be confidently located are None.
    """
    reader, backend = _get_reader()
    raw_lines: list[str] = []
    line_boxes: list[dict] = []

    if backend == "easyocr" and reader is not None:
        results = reader.readtext(image_path)
        for bbox, text, conf in results:
            raw_lines.append(text)
            line_boxes.append({"text": text, "confidence": round(float(conf), 3), "bbox": bbox})
    else:
        # Tesseract fallback
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        raw_text_block = pytesseract.image_to_string(img)
        raw_lines = [ln for ln in raw_text_block.splitlines() if ln.strip()]
        line_boxes = [{"text": ln, "confidence": None, "bbox": None} for ln in raw_lines]

    raw_text = "\n".join(raw_lines)

    result = OCRResult(
        raw_text=raw_text,
        amount=_extract_field(AMOUNT_RE, raw_text),
        date=_extract_field(DATE_RE, raw_text),
        time=_extract_field(TIME_RE, raw_text),
        utr=_extract_field(UTR_RE, raw_text),
        bank_name=_extract_bank(raw_text),
        payment_status=_extract_status(raw_text),
        line_boxes=line_boxes,
    )
    result.sender_upi, result.receiver_upi = _extract_upi_ids(raw_text)
    return result
