# Fake Payment Detector AI — Project Documentation

## Overview

Fake Payment Detector AI is a forensic analysis platform for UPI payment screenshots.
Users upload a screenshot; the system runs OCR to extract the printed
payment details, then runs a battery of computer-vision forensic checks and
a CNN-based classifier to estimate how likely the image is to have been
digitally edited. The result is an explainable 0–100% confidence score with
a plain-language breakdown of every check performed.

## Scope & Disclaimer

This project deliberately stops at **image forensics**. It:

- **Does** read the text printed in a screenshot (OCR).
- **Does** analyze the image file itself for editing artifacts (compression
  inconsistency, copy-paste duplication, font mismatches, blur anomalies,
  metadata anomalies, crop plausibility, QR structural validity).
- **Does** combine those signals into an explainable confidence score.
- **Does not** contact any bank, payment gateway, UPI switch, or NPCI
  system.
- **Does not** have access to, or claim to confirm, real account balances
  or settlement status.
- **Does not** guarantee a transaction is fake or genuine — it surfaces
  statistical evidence for a human to weigh, the same way classical digital
  forensics tooling works.

Real transaction verification requires regulated institutional access to
NPCI/bank rails. That integration is explicitly listed under **Future
Scope** as an extension point, not something this project simulates or
claims to provide.

## Feature Summary

1. **Landing Page** — hero, feature cards, architecture diagram, About the
   AI, Future Scope (`frontend/src/pages/LandingPage.tsx`)
2. **Authentication** — register / login / forgot-password / JWT access +
   refresh tokens (`backend/app/api/routes/auth.py`)
3. **Dashboard** — total analyses, suspicious/genuine counts, average
   confidence, pie chart, bar chart, timeline (`DashboardPage.tsx` +
   `/analysis/stats/dashboard`)
4. **Upload** — drag-and-drop, PNG/JPG/JPEG, live preview
   (`UploadPage.tsx`)
5. **OCR Module** — amount, date, time, UTR, bank, sender/receiver UPI ID,
   payment status (`ai/ocr/extractor.py`)
6. **AI Forensic Analysis** — 9 checks + CNN signal
   (`ai/forensics/analyzer.py`, `ai/models/cnn_classifier.py`)
7. **Confidence Score** — 0–100% with 3-tier verdict
   (`ai/utils/confidence.py`)
8. **Explainability** — pass/fail checklist per analysis
9. **History** — search, sort, filter, delete (`HistoryPage.tsx`)
10. **Export Report** — downloadable PDF
    (`backend/app/services/pdf_report_service.py`)
11. **Admin Dashboard** — user management, stats, system logs
    (`AdminPage.tsx`, `backend/app/api/routes/admin.py`)
12. **API Documentation** — Swagger UI at `/api/docs`
13. **Security** — rate limiting (SlowAPI), input validation (Pydantic +
    magic-byte checks), file size limits, JWT auth with bcrypt hashing
14. **Future Scope** — see below

## Future Scope

- Official NPCI/bank-partner API integration for real settlement
  verification (requires regulated institutional access, out of scope for
  this academic project)
- Training the bundled CNN architecture to convergence on a labeled
  genuine/manipulated screenshot dataset (`ai/models/train.py`)
- On-device capture to avoid re-compression noise from screenshot sharing
- Multi-language OCR for regional payment apps
- Browser extension / mobile app front-ends reusing the same backend API

## Repository Map

See the root [`README.md`](../README.md#project-structure) for the full
directory tree.
