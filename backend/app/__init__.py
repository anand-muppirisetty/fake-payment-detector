"""
AI-Powered Fake Payment Detection System — Backend Application Package.

This package contains the FastAPI application responsible for:
- User authentication (JWT based)
- Payment screenshot upload & storage
- Orchestrating OCR + forensic AI analysis (see the top-level `ai/` package)
- Persisting analysis results to PostgreSQL
- Serving history, dashboard statistics, admin operations and PDF report export

IMPORTANT SCOPE NOTE:
This system performs *forensic image analysis* of payment screenshots only.
It does NOT connect to any bank, UPI switch, or NPCI system, and it never
claims to confirm whether a transaction actually settled. See
docs/README.md -> "Scope & Disclaimer" for details.
"""
