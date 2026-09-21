"""
Rule-based + classical computer-vision forensic analysis for UPI payment
screenshots.

Each check below is a self-contained heuristic built on OpenCV / NumPy /
scikit-image signal-processing techniques (error-level analysis style
compression-artifact detection, edge/font-consistency checks, ELA-based
copy-paste localization, EXIF/metadata inspection, blur-variance mapping,
QR code structural validation, crop/aspect-ratio plausibility).

None of these checks contact any bank or NPCI system, and none of them can
prove a transaction is fraudulent with certainty — they surface signals that
a human reviewer (or the confidence-scoring layer) can weigh. This mirrors
how real digital-image-forensics tooling works: statistical anomaly
detection, not ground-truth verification.

The CNN-based classifier in ai/models/cnn_classifier.py is wired in as an
additional signal (placeholder architecture per project spec) — its output
is combined with these rule-based findings in `run_forensic_analysis`.
"""
from __future__ import annotations

import io
import logging
from dataclasses import asdict, dataclass
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ExifTags

logger = logging.getLogger(__name__)


@dataclass
class Finding:
    code: str
    label: str
    detected: bool
    severity: str          # low | medium | high
    detail: str
    score_impact: float     # negative = lowers confidence, positive = raises it


# --------------------------------------------------------------------------
# Individual forensic checks
# --------------------------------------------------------------------------

def check_compression_artifacts(img_bgr: np.ndarray) -> Finding:
    """
    Error Level Analysis (ELA)-style check: re-encode the image at a known
    JPEG quality and diff against the original. Regions that were pasted in
    from a different generation/compression history "light up" with a
    different error level than the rest of the image, which is a classic
    tell for screenshot editing.
    """
    ok, encoded = cv2.imencode(".jpg", img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        return Finding("COMPRESSION_ARTIFACTS", "Compression artifacts", False, "low",
                        "Could not re-encode image for ELA comparison.", 0.0)
    recompressed = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if recompressed.shape != img_bgr.shape:
        recompressed = cv2.resize(recompressed, (img_bgr.shape[1], img_bgr.shape[0]))
    diff = cv2.absdiff(img_bgr, recompressed)
    error_level = float(np.mean(diff))
    # Compute local variance of the error map — a real screenshot re-saved
    # once tends to have a fairly *uniform* low error level; a spliced
    # region shows a patch of unusually high local error.
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    local_std = float(np.std(gray_diff))
    detected = local_std > 14.0 or error_level > 9.0
    severity = "high" if local_std > 20 else ("medium" if detected else "low")
    return Finding(
        "COMPRESSION_ARTIFACTS", "Compression artifacts", detected, severity,
        f"ELA error-level std={local_std:.2f}, mean={error_level:.2f} (thresholds: std>14, mean>9).",
        -12.0 if detected else 3.0,
    )


def check_copy_paste_artifacts(img_bgr: np.ndarray) -> Finding:
    """
    Detects duplicated regions (copy-move forgery) using ORB keypoint
    matching: legitimate screenshots rarely contain two visually-identical
    patches of texture/text, whereas a pasted-over amount often reuses
    cloned background pixels around its edges.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=800)
    kp, des = orb.detectAndCompute(gray, None)
    if des is None or len(kp) < 20:
        return Finding("COPY_PASTE_ARTIFACTS", "Copy-paste artifacts", False, "low",
                        "Not enough keypoints to evaluate duplication.", 0.0)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des, des, k=3)  # k=3 because best match of a point is itself
    duplicate_pairs = 0
    for m in matches:
        if len(m) < 3:
            continue
        _self, second, third = m
        # self-match (distance 0) skipped; look at next-best distinct match
        if second.distance < 20 and second.trainIdx != second.queryIdx:
            pt1 = np.array(kp[second.queryIdx].pt)
            pt2 = np.array(kp[second.trainIdx].pt)
            if np.linalg.norm(pt1 - pt2) > 15:  # not just adjacent identical texture
                duplicate_pairs += 1
    ratio = duplicate_pairs / max(len(kp), 1)
    detected = ratio > 0.05
    severity = "high" if ratio > 0.12 else ("medium" if detected else "low")
    return Finding(
        "COPY_PASTE_ARTIFACTS", "Copy-paste artifacts", detected, severity,
        f"{duplicate_pairs} duplicated keypoint clusters found ({ratio*100:.1f}% of keypoints).",
        -15.0 if detected else 2.0,
    )


def check_font_inconsistency(img_bgr: np.ndarray) -> Finding:
    """
    Measures stroke-width consistency across text regions. Genuine app
    screenshots render all text with one rendering engine/font, giving
    fairly uniform stroke widths; text edited in an external tool (or
    pasted from a different app) tends to show a different stroke-width
    distribution in the edited region.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 150)
    # distance transform gives an approximate local stroke-width map
    dist = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 3)
    text_like = dist[(dist > 0) & (dist < 6)]
    if text_like.size < 200:
        return Finding("FONT_INCONSISTENCY", "Font inconsistencies", False, "low",
                        "Insufficient text-like edge data to assess font consistency.", 0.0)
    stroke_std = float(np.std(text_like))
    detected = stroke_std > 1.55
    severity = "high" if stroke_std > 1.9 else ("medium" if detected else "low")
    return Finding(
        "FONT_INCONSISTENCY", "Font inconsistencies", detected, severity,
        f"Stroke-width std deviation={stroke_std:.2f} (threshold 1.55).",
        -13.0 if detected else 4.0,
    )


def check_blur_inconsistency(img_bgr: np.ndarray) -> Finding:
    """
    Splits the image into a grid and computes the Laplacian variance
    (a standard sharpness/blur metric) per cell. A screenshot is normally
    uniformly sharp; a locally blurred patch (used to smooth over an edit)
    stands out as a low-variance outlier cell surrounded by sharp ones.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    rows, cols = 6, 4
    cell_h, cell_w = max(h // rows, 1), max(w // cols, 1)
    variances = []
    for r in range(rows):
        for c in range(cols):
            cell = gray[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w]
            if cell.size == 0:
                continue
            variances.append(cv2.Laplacian(cell, cv2.CV_64F).var())
    if len(variances) < 6:
        return Finding("BLUR_INCONSISTENCY", "Blur inconsistencies", False, "low",
                        "Grid too small to evaluate blur consistency.", 0.0)
    variances = np.array(variances)
    median = np.median(variances)
    outliers = np.sum(variances < (median * 0.15)) if median > 5 else 0
    detected = bool(outliers >= 1 and median > 15)
    severity = "high" if outliers >= 3 else ("medium" if detected else "low")
    return Finding(
        "BLUR_INCONSISTENCY", "Blur inconsistencies", detected, severity,
        f"{int(outliers)} unusually blurred region(s) out of {len(variances)} grid cells "
        f"(median sharpness={median:.1f}).",
        -10.0 if detected else 2.0,
    )


def check_metadata_anomalies(image_bytes: bytes) -> Finding:
    """
    Inspects EXIF metadata. Real phone-camera photos usually carry rich
    EXIF (device model, timestamps); pure app screenshots typically carry
    little/no EXIF by design, so this check mainly flags *contradictions*
    (e.g. a "Software" tag naming a known photo editor) rather than
    "missing EXIF" alone, since missing EXIF is normal for screenshots.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_raw = img._getexif() if hasattr(img, "_getexif") else None
    except Exception:
        exif_raw = None

    editor_signatures = ["photoshop", "gimp", "snapseed", "picsart", "lightroom", "pixlr", "canva"]
    detected = False
    detail = "No EXIF metadata present (typical for direct app screenshots)."
    if exif_raw:
        tags = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
        software = str(tags.get("Software", "")).lower()
        if any(sig in software for sig in editor_signatures):
            detected = True
            detail = f"EXIF 'Software' tag references an image editor: '{tags.get('Software')}'."
        else:
            detail = f"EXIF metadata present ({len(tags)} tags); no editor signature found."
    return Finding(
        "METADATA_ANOMALY", "Metadata anomalies", detected, "high" if detected else "low",
        detail, -20.0 if detected else 1.0,
    )


def check_screenshot_cropping(img_bgr: np.ndarray) -> Finding:
    """
    Flags implausible aspect ratios / hard color-block borders that suggest
    a screenshot was cropped tightly around a manipulated region rather
    than captured as a normal full-screen shot.
    """
    h, w = img_bgr.shape[:2]
    aspect = h / max(w, 1)
    # Typical phone full-screenshots: aspect roughly 1.6 - 2.5 (portrait)
    implausible_aspect = not (1.3 <= aspect <= 2.6)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    border = 4
    top = gray[:border, :]
    bottom = gray[-border:, :]
    left = gray[:, :border]
    right = gray[:, -border:]
    border_std = float(np.mean([np.std(top), np.std(bottom), np.std(left), np.std(right)]))
    hard_cut_border = border_std < 2.0  # suspiciously flat/uniform border = possible hard crop

    detected = bool(implausible_aspect or hard_cut_border)
    severity = "medium" if detected else "low"
    return Finding(
        "SCREENSHOT_CROPPING", "Screenshot cropping", detected, severity,
        f"aspect_ratio={aspect:.2f} (expected ~1.3-2.6), border_flatness_std={border_std:.2f}.",
        -8.0 if detected else 2.0,
    )


def check_qr_code(img_bgr: np.ndarray) -> Finding:
    """
    Attempts to locate and decode a QR code (common on payment-success
    screens). If a QR is present, we structurally validate it can be
    decoded and is positioned/sized plausibly; a QR that is visually
    present but fails to decode, or is oddly warped/pixelated compared to
    surrounding UI sharpness, is a red flag consistent with a pasted-in
    fake QR image.
    """
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img_bgr)
    if points is None:
        return Finding("FAKE_QR_CODE", "Fake QR code", False, "low",
                        "No QR code detected in image (not applicable).", 0.0)
    decoded_ok = bool(data)
    # Check local sharpness of the QR region vs rest of image
    pts = points.reshape(-1, 2).astype(int)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    x_min, y_min = max(x_min, 0), max(y_min, 0)
    qr_patch = img_bgr[y_min:y_max, x_min:x_max]
    detected = False
    detail = "QR code detected and decoded successfully."
    if not decoded_ok:
        detected = True
        detail = "QR code region detected but could not be decoded — possible fake/corrupted QR image."
    elif qr_patch.size > 0:
        qr_gray = cv2.cvtColor(qr_patch, cv2.COLOR_BGR2GRAY)
        qr_sharpness = cv2.Laplacian(qr_gray, cv2.CV_64F).var()
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        overall_sharpness = cv2.Laplacian(img_gray, cv2.CV_64F).var()
        if overall_sharpness > 5 and qr_sharpness < (overall_sharpness * 0.25):
            detected = True
            detail = (f"QR decodes but is markedly softer than surrounding UI "
                       f"(qr={qr_sharpness:.1f} vs overall={overall_sharpness:.1f}) — "
                       "consistent with a pasted-in QR image.")
    return Finding(
        "FAKE_QR_CODE", "Fake QR code", detected, "high" if detected else "low",
        detail, -18.0 if detected else 5.0,
    )


def check_edited_amount_region(img_bgr: np.ndarray, ocr_amount: Optional[str]) -> Finding:
    """
    If OCR found an amount, inspect the local pixel neighborhood around
    the highest-contrast text cluster in the upper-middle portion of the
    screenshot (where amounts are typically displayed) for double-edge /
    halo artifacts that indicate text was overlaid on the image after
    the fact (common when someone edits the amount using a photo editor).
    """
    if not ocr_amount:
        return Finding("EDITED_AMOUNT", "Edited amount", False, "low",
                        "No amount text detected by OCR to inspect.", 0.0)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    roi = gray[int(h * 0.15):int(h * 0.45), :]  # amount typically near top of success screen
    if roi.size == 0:
        return Finding("EDITED_AMOUNT", "Edited amount", False, "low", "ROI empty.", 0.0)
    edges = cv2.Canny(roi, 50, 150)
    double_edge_kernel = np.array([[1, 0, 1]], dtype=np.uint8)
    dilated = cv2.dilate(edges, double_edge_kernel, iterations=1)
    halo_ratio = float(np.sum(dilated > 0)) / max(edges.size, 1)
    detected = halo_ratio > 0.18
    return Finding(
        "EDITED_AMOUNT", "Edited amount", detected, "high" if detected else "low",
        f"Halo/double-edge pixel ratio around amount region={halo_ratio:.3f} (threshold 0.18).",
        -22.0 if detected else 4.0,
    )


def check_utr_format(ocr_utr: Optional[str]) -> Finding:
    """
    Validates that the extracted UTR/reference number matches the expected
    length/character-class pattern used by UPI rails (12-22 alphanumeric
    characters, typically digits). This is a *format* plausibility check
    only — it never contacts NPCI/any bank to confirm the UTR is real.
    """
    if not ocr_utr:
        return Finding("UTR_FORMAT", "UTR format valid", False, "medium",
                        "No UTR/reference number could be extracted by OCR.", -6.0)
    is_valid_len = 9 <= len(ocr_utr) <= 22
    is_alnum = ocr_utr.isalnum()
    detected_invalid = not (is_valid_len and is_alnum)
    return Finding(
        "UTR_FORMAT", "UTR format valid", detected_invalid, "medium" if detected_invalid else "low",
        f"UTR '{ocr_utr}' length={len(ocr_utr)}, alnum={is_alnum}.",
        -9.0 if detected_invalid else 6.0,
    )


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def run_forensic_analysis(image_path: str, image_bytes: bytes, ocr_amount: Optional[str],
                           ocr_utr: Optional[str]) -> list[Finding]:
    """
    Run the full forensic checklist against the uploaded image and return
    a list of Finding objects. Also folds in the CNN placeholder classifier
    signal (see ai/models/cnn_classifier.py).
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError("Unable to read image for forensic analysis (unsupported/corrupt file).")

    findings: list[Finding] = [
        check_compression_artifacts(img_bgr),
        check_copy_paste_artifacts(img_bgr),
        check_font_inconsistency(img_bgr),
        check_blur_inconsistency(img_bgr),
        check_metadata_anomalies(image_bytes),
        check_screenshot_cropping(img_bgr),
        check_qr_code(img_bgr),
        check_edited_amount_region(img_bgr, ocr_amount),
        check_utr_format(ocr_utr),
    ]

    # CNN placeholder signal (lazy import keeps torch optional at import time)
    try:
        from ai.models.cnn_classifier import classify_manipulation_probability
        cnn_prob = classify_manipulation_probability(img_bgr)
        findings.append(Finding(
            "CNN_MANIPULATION_SCORE", "CNN-based manipulation likelihood",
            detected=cnn_prob > 0.5, severity="high" if cnn_prob > 0.7 else "medium" if cnn_prob > 0.5 else "low",
            detail=f"CNN classifier manipulation probability={cnn_prob:.2f} (placeholder architecture).",
            score_impact=-25.0 * cnn_prob if cnn_prob > 0.5 else (1 - cnn_prob) * 5,
        ))
    except Exception as exc:  # pragma: no cover
        logger.warning("CNN classifier unavailable: %s", exc)

    return findings


def findings_to_dicts(findings: list[Finding]) -> list[dict]:
    return [asdict(f) for f in findings]
