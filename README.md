# 🔍 Fake Payment Detector AI

**An AI-powered forensic analysis system that examines UPI payment screenshots for signs of digital manipulation, using OCR and computer vision — without ever connecting to real banking systems.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)

---

## 📌 Overview

UPI payment screenshots are commonly shared as informal proof of payment — and just as commonly edited using photo editors to fake amounts or transaction statuses. This project is a full-stack application that lets a user upload such a screenshot and receive an automated **forensic analysis** of the image itself: OCR-extracted payment details, a set of computer-vision checks looking for editing artifacts, and an explainable confidence score summarizing the findings.

The system does **not** connect to any bank, UPI switch, or NPCI infrastructure, and does not verify whether a transaction actually settled — it strictly analyzes the uploaded image for signs of digital tampering, similar in principle to classical image-forensics tooling.

This project was built to apply full-stack development and applied computer-vision/OCR techniques to a real-world, socially relevant problem, and to practice designing a system where AI output is explainable rather than a black-box verdict.

---

## ✨ Key Features

- **OCR Extraction** — reads amount, date, time, UTR/reference number, bank name, sender/receiver UPI ID, and payment status directly from the screenshot using EasyOCR (with a Tesseract fallback)
- **Forensic Image Analysis** — nine independent OpenCV/scikit-image-based checks: compression-artifact (ELA-style) detection, copy-paste/duplicate-region detection via ORB keypoint matching, font/stroke-width consistency, blur-inconsistency mapping, EXIF metadata inspection, crop plausibility, QR code structural validation, edited-amount halo detection, and UTR format validation
- **CNN Signal (placeholder architecture)** — a real, trainable PyTorch CNN is wired into the pipeline as specified in the project brief; since no labeled training dataset exists yet, it currently runs on an explainable heuristic fallback rather than trained weights (a training script is included for future use)
- **Explainable Confidence Score** — all check outputs are combined by a rule-based scoring algorithm into a 0–100% score with a three-tier verdict (Likely Genuine / Needs Manual Review / Highly Suspicious), along with a plain-language pass/fail checklist
- **Authentication** — JWT-based register/login/forgot-password flow with bcrypt password hashing
- **Dashboard** — summary stats and charts (pie, bar, timeline) built from a user's own analysis history
- **History Management** — search, sort, filter, and delete past analyses
- **PDF Report Export** — generates a downloadable forensic report (screenshot, OCR data, findings, score) using ReportLab
- **Admin Panel** — user management, system-wide statistics, and an audit log of key events
- **Rate Limiting & Input Validation** — upload size/type validation, magic-byte checks, and per-route rate limiting via SlowAPI

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| **Language** | Python, TypeScript |
| **Frontend** | React, Tailwind CSS, Framer Motion, Recharts |
| **Backend** | FastAPI, JWT Auth (python-jose), Passlib/bcrypt, SlowAPI |
| **Database** | PostgreSQL, SQLAlchemy, Alembic |
| **AI / Computer Vision** | EasyOCR, Tesseract (fallback), OpenCV, scikit-image, PyTorch |
| **Reporting** | ReportLab (PDF generation) |
| **Tools** | Docker, Docker Compose, Vite, pytest |

---

## 🏗️ Project Architecture

```mermaid
flowchart LR
    A[User] --> B[React Frontend]
    B -->|REST + JWT| C[FastAPI Backend]
    C --> D[Storage: UUID-named files]
    C --> E[OCR Extraction]
    E --> F[Forensic CV Checks]
    F --> G[CNN Signal]
    G --> H[Confidence Scoring]
    H --> I[(PostgreSQL)]
    I --> B
```

The frontend communicates with the backend exclusively through a versioned REST API. The AI pipeline (`ai/`) is a self-contained Python package independent of the web framework, so OCR, forensic checks, and scoring can be tested or reused without running the API server.

---

## 📂 Project Structure
fake-payment-detector/
├── frontend/ React + TypeScript + Tailwind CSS SPA
│ └── src/
│ ├── pages/ Landing, Auth, Dashboard, Upload, History, Admin
│ ├── components/ Reusable UI components
│ ├── context/ Auth & Theme context providers
│ └── services/ Axios API client
├── backend/ FastAPI application
│ ├── app/
│ │ ├── api/routes/ auth, analysis, admin routers
│ │ ├── core/ config, database, security, rate limiting
│ │ ├── models/ SQLAlchemy models (User, Analysis, SystemLog)
│ │ ├── schemas/ Pydantic request/response schemas
│ │ └── services/ storage, PDF report, analysis orchestration
│ └── tests/ pytest unit tests
├── ai/ AI pipeline (framework-independent)
│ ├── ocr/ OCR extraction & field parsing
│ ├── forensics/ Computer-vision forensic checks
│ ├── models/ CNN classifier + training script
│ └── utils/ Confidence scoring algorithm
├── database/ Alembic migration environment
├── docs/ Architecture, ER, and sequence diagrams; API & deployment docs
└── docker-compose.yml Postgres + backend + frontend stack

---

## ⚙️ How It Works

1. The user registers/logs in and uploads a UPI payment screenshot (PNG/JPG) via drag-and-drop.
2. The backend validates the file (type, size, magic bytes) and stores it under a UUID-generated filename.
3. The OCR module extracts raw text and parses structured fields (amount, UTR, bank name, UPI IDs, etc.).
4. The forensic module runs nine OpenCV-based checks plus the CNN signal against the image.
5. The confidence-scoring algorithm combines all check results into a 0–100% score and a verdict label.
6. The result — OCR data, findings, score, and an explainability checklist — is saved to PostgreSQL and returned to the frontend.
7. The user can view the result on the dashboard, browse it later in History, or export it as a PDF report.

---

## 🚀 Installation & Setup

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/fake-payment-detector.git
cd fake-payment-detector
```

### Option A — Docker (recommended)

```bash
docker compose up --build
```

This starts PostgreSQL, the FastAPI backend, and the React frontend together.

### Option B — Manual setup

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Environment Variables

Backend `.env` (see `backend/.env.example`):
DATABASE_URL=postgresql://fpd_user:fpd_password@localhost:5432/fake_payment_detector
SECRET_KEY=replace-with-a-long-random-secret-string
CORS_ORIGINS=["http://localhost:5173"]
Frontend `.env` (see `frontend/.env.example`):

VITE_API_BASE_URL=/api/v1


No real credentials are committed to the repository — both `.env.example` files must be copied and filled in locally.

---

## ▶️ Usage

```bash
docker compose up
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend + Swagger Docs | http://localhost:8000/api/docs |

Create an admin account:
```bash
docker compose exec backend python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
```

After starting the stack, register an account on the frontend, upload a screenshot on the Analyze page, and the confidence score, verdict, and explainability checklist will be displayed once processing completes.

---

## 📊 Results / Output

Each analysis returns:
- Extracted OCR fields (amount, date, time, UTR, bank name, UPI IDs, payment status)
- A confidence score (0–100%) and verdict (Likely Genuine / Needs Manual Review / Highly Suspicious)
- A per-check breakdown (which forensic checks passed or were flagged, and why)
- A downloadable PDF report of the above

### 📸 Screenshots

_Add screenshots here._

---

## 🧪 Testing

The project includes a `pytest` suite under `backend/tests/` covering the core business logic:
- **`test_confidence.py`** — verifies the confidence-scoring algorithm produces correct verdicts for clean vs. heavily-flagged inputs, and that scores are correctly clamped to the 0–100 range
- **`test_ocr_patterns.py`** — verifies the regex-based OCR field parsers correctly extract amount, UTR, status, and bank name from sample text

Run with:
```bash
cd backend
pytest tests/
```

---

## 🔮 Future Improvements

- Train the bundled CNN classifier (`ai/models/train.py`) on a labeled dataset of genuine vs. manipulated screenshots, replacing the current heuristic fallback
- Official NPCI/bank-partner API integration for real settlement verification (requires regulated institutional access, currently out of scope)
- Multi-language OCR support for regional payment apps
- Deployment to a public cloud environment with object storage for uploads
- CI pipeline for automated testing on push

---

## 🎯 Learning Outcomes

Building this project involved:
- Designing and implementing a full-stack application with a React/TypeScript frontend and a FastAPI backend
- Implementing JWT-based authentication and password hashing
- Applying OCR (EasyOCR/Tesseract) and classical computer-vision techniques (OpenCV, scikit-image) to a practical image-forensics problem
- Designing a rule-based scoring system that aggregates multiple independent signals into an explainable output
- Structuring a relational database schema (PostgreSQL) and managing it with SQLAlchemy and Alembic
- Containerizing a multi-service application with Docker Compose
- Writing unit tests for core business logic with pytest

---

## 👨‍💻 Author

**Anand Kumar Muppirisetty**

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anand-kumar-muppirisetty-884a59315)
[![Gmail](https://img.shields.io/badge/Gmail-Contact_Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:anandkumar.muppirisetty@gmail.com)

</div>

<br/>

---

## 📄 License

License information can be added based on the intended distribution of the project.

---

⭐ If you found this project useful, consider giving the repository a star.
