"""
Generates a downloadable PDF forensic report for a single analysis, using
reportlab. Includes: screenshot thumbnail, extracted OCR text, forensic
findings table, confidence score/verdict, and timestamp.
"""
from __future__ import annotations

import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from app.models.analysis import Analysis


def _verdict_color(verdict: str):
    return {
        "Likely Genuine": colors.HexColor("#16a34a"),
        "Needs Manual Review": colors.HexColor("#d97706"),
        "Highly Suspicious": colors.HexColor("#dc2626"),
    }.get(verdict, colors.black)


def generate_report_pdf(analysis: Analysis, image_abs_path: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#0f172a"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#0f172a"))
    body = styles["BodyText"]
    mono = ParagraphStyle("Mono", parent=styles["BodyText"], fontName="Courier", fontSize=8, leading=10)

    story = []
    story.append(Paragraph("AI-Powered Fake Payment Detection System", title_style))
    story.append(Paragraph("Forensic Analysis Report", h2))
    story.append(Paragraph(
        "This report reflects an automated forensic image analysis only. It does NOT constitute "
        "confirmation of a real bank transaction and is not sourced from any bank or NPCI system.",
        ParagraphStyle("Disclaimer", parent=body, textColor=colors.HexColor("#b91c1c"), fontSize=8),
    ))
    story.append(Spacer(1, 8 * mm))

    if os.path.exists(image_abs_path):
        try:
            story.append(RLImage(image_abs_path, width=90 * mm, height=90 * mm, kind="proportional"))
        except Exception:
            pass
    story.append(Spacer(1, 6 * mm))

    verdict_color = _verdict_color(analysis.verdict.value if hasattr(analysis.verdict, "value") else analysis.verdict)
    verdict_style = ParagraphStyle("Verdict", parent=styles["Heading2"], textColor=verdict_color)
    story.append(Paragraph(f"Confidence Score: {analysis.confidence_score:.1f}%", verdict_style))
    verdict_text = analysis.verdict.value if hasattr(analysis.verdict, "value") else analysis.verdict
    story.append(Paragraph(f"Verdict: {verdict_text}", verdict_style))
    story.append(Paragraph(f"Report generated: {analysis.created_at.strftime('%d %b %Y, %H:%M UTC')}", body))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Extracted OCR Fields", h2))
    ocr_rows = [
        ["Field", "Value"],
        ["Amount", analysis.ocr_amount or "—"],
        ["Date", analysis.ocr_date or "—"],
        ["Time", analysis.ocr_time or "—"],
        ["UTR / Reference No.", analysis.ocr_utr or "—"],
        ["Bank Name", analysis.ocr_bank_name or "—"],
        ["Sender UPI ID", analysis.ocr_sender_upi or "—"],
        ["Receiver UPI ID", analysis.ocr_receiver_upi or "—"],
        ["Payment Status (as printed)", analysis.ocr_payment_status or "—"],
    ]
    ocr_table = Table(ocr_rows, colWidths=[55 * mm, 100 * mm])
    ocr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ocr_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("AI Forensic Findings", h2))
    finding_rows = [["Check", "Result", "Severity", "Detail"]]
    for f in (analysis.forensic_findings or []):
        finding_rows.append([
            f.get("label", ""),
            "Flagged" if f.get("detected") else "Passed",
            f.get("severity", ""),
            Paragraph(f.get("detail", ""), mono),
        ])
    findings_table = Table(finding_rows, colWidths=[38 * mm, 20 * mm, 20 * mm, 77 * mm])
    findings_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Extracted Raw OCR Text", h2))
    raw_text = (analysis.ocr_raw_text or "—").replace("\n", "<br/>")
    story.append(Paragraph(raw_text, mono))

    doc.build(story)
    return buffer.getvalue()
