"""Unit tests for the regex-based OCR field parsers (pure string logic, no image needed)."""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from ai.ocr.extractor import _extract_field, _extract_status, _extract_bank, AMOUNT_RE, UTR_RE


def test_amount_extraction():
    text = "Payment Successful\n₹1,250.00\nTo: merchant@okhdfcbank"
    assert _extract_field(AMOUNT_RE, text) == "1,250.00"


def test_utr_extraction():
    text = "UPI Ref No: 402812345678\nStatus: Success"
    utr = _extract_field(UTR_RE, text)
    assert utr == "402812345678"


def test_status_extraction():
    assert _extract_status("Transaction Successful") == "Success"
    assert _extract_status("Payment Failed") == "Failed"


def test_bank_extraction():
    assert _extract_bank("Paid via HDFC Bank UPI") == "HDFC Bank"
