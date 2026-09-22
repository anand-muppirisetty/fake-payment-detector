<div align="center">

# 🔍 Fake Payment Detector AI

**AI-powered forensic analysis for UPI payment screenshots.**
OCR + Computer Vision + Explainable Confidence Scoring — built as a final-year B.Tech AI & ML project.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

</div>

---

## ⚠️ Scope & Disclaimer

**This project does not verify real bank transactions.** It performs **forensic image
analysis** of a screenshot the user uploads — OCR text extraction plus classical
computer-vision and CNN-based manipulation detection — to produce an explainable
confidence score describing how likely the *image* is to have been digitally edited.

It never contacts a bank, UPI switch, or NPCI system, has no access to real
account/transaction data, and its verdict should not be treated as legal or
financial proof. Real transaction verification would require regulated
institutional API access — intentionally out of scope for this academic project
(see **Future Scope** below).

---

## ✨ Features

| Area | What it does |
|---|---|
| 🏠 **Landing Page** | Hero section, feature cards, architecture diagram, About the AI, Future Scope |
| 🔐 **Authentication** | Register, login, forgot/reset password — JWT access + refresh tokens |
| 📊 **Dashboard** | Total analyses, suspicious/genuine counts, average confidence, pie chart, bar chart, timeline |
| 📤 **Upload** | Drag-and-drop PNG/JPG/JPEG with live preview |
| 🔤 **OCR Module** | Extracts amount, date, time, UTR, bank name, sender/receiver UPI ID, payment status |
| 🕵️ **AI Forensic Analysis** | 9 checks: font inconsistency, copy-paste artifacts, compression artifacts, edited amount, fake QR, metadata anomalies, cropping, blur inconsistency, + CNN signal |
| 🎯 **Confidence Score** | 0–100% score with a 3-tier verdict (Likely Genuine / Needs Manual Review / Highly Suspicious) |
| 💡 **Explainability** | Plain-language checklist of exactly why a screenshot was flagged |
| 🕘 **History** | Search, sort, filter, delete past analyses |
| 📄 **Export Report** | Downloadable PDF with screenshot, extracted text, findings, and score |
| 🛡️ **Admin Dashboard** | User management, system-wide stats, audit logs |
| 📚 **API Docs** | Auto-generated Swagger UI at `/api/docs` |
| 🔒 **Security** | Rate limiting, input validation, file size limits, JWT + bcrypt |

---

## 🖥️ Tech Stack

- **Frontend:** React, TypeScript, Tailwind CSS, Framer Motion, Recharts
- **Backend:** Python, FastAPI, JWT auth, SlowAPI rate limiting
- **AI:** EasyOCR / Tesseract, OpenCV, scikit-image, PyTorch (placeholder CNN architecture), rule-based confidence scoring
- **Database:** PostgreSQL via SQLAlchemy + Alembic
- **Storage:** Local disk, UUID-named files

---

## 🚀 Quick Start

\`\`\`bash
git clone https://github.com/<your-username>/fake-payment-detector.git
cd fake-payment-detector
docker compose up --build
\`\`\`

- Frontend → **http://localhost:5173**
- Backend API + Swagger docs → **http://localhost:8000/api/docs**

Create your first admin account:
\`\`\`bash
docker compose exec backend python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
\`\`\`

📖 Full setup instructions (with or without Docker): [\`docs/INSTALLATION.md\`](docs/INSTALLATION.md)

---

## 📁 Project Structure

\`\`\`
fake-payment-detector/
├── frontend/          React + TypeScript + Tailwind CSS SPA
├── backend/            FastAPI REST API (auth, uploads, history, admin)
├── ai/                 OCR, forensic CV checks, CNN classifier, confidence scoring
├── database/            Alembic migrations (PostgreSQL schema)
├── docs/                Full documentation set
└── docker-compose.yml   One-command local stack (Postgres + backend + frontend)
\`\`\`

---

## 📚 Documentation

| Doc | Purpose |
|---|---|
| [\`docs/README.md\`](docs/README.md) | Full project overview & scope disclaimer |
| [\`docs/INSTALLATION.md\`](docs/INSTALLATION.md) | Local setup guide |
| [\`docs/API_DOCUMENTATION.md\`](docs/API_DOCUMENTATION.md) | REST API reference |
| [\`docs/diagrams/architecture.md\`](docs/diagrams/architecture.md) | System architecture diagram |
| [\`docs/diagrams/er-diagram.md\`](docs/diagrams/er-diagram.md) | Database ER diagram |
| [\`docs/diagrams/sequence-diagram.md\`](docs/diagrams/sequence-diagram.md) | Upload → analysis sequence diagram |
| [\`docs/DEPLOYMENT.md\`](docs/DEPLOYMENT.md) | Deployment guide |
| [\`HOW_TO_RUN.md\`](HOW_TO_RUN.md) | Quick day-to-day run instructions |

---

## 🔮 Future Scope

- Official NPCI/bank-partner API integration for real settlement verification (requires regulated institutional access)
- Training the bundled CNN classifier to convergence on a labeled genuine/manipulated screenshot dataset (\`ai/models/train.py\`)
- On-device capture to reduce screenshot re-compression noise
- Multi-language OCR support for regional payment apps
- Browser extension / mobile app front-ends reusing the same backend API

---

## 📄 License

This project is built for educational purposes as a final-year B.Tech AI & ML project.
