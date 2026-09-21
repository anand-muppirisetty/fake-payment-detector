# Installation Guide

Two paths: Docker (fastest) or manual local setup (better for development /
debugging on a final-year project machine).

## Option A — Docker Compose (recommended)

Prerequisites: Docker + Docker Compose.

```bash
git clone <this-repo>
cd fake-payment-detector
docker compose up --build
```

This starts PostgreSQL, the FastAPI backend (`:8000`) and the React
frontend (`:5173`). Tables are created automatically on backend startup.

Create your first admin account:

```bash
docker compose exec backend python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
```

## Option B — Manual Local Setup

### 1. PostgreSQL

Install PostgreSQL 14+ locally, then:

```sql
CREATE USER fpd_user WITH PASSWORD 'fpd_password';
CREATE DATABASE fake_payment_detector OWNER fpd_user;
```

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edit DATABASE_URL / SECRET_KEY as needed
uvicorn app.main:app --reload --port 8000
```

The app creates all tables automatically on first startup (via
`Base.metadata.create_all`). For production, prefer Alembic migrations:

```bash
alembic upgrade head
```

Create an admin user:

```bash
python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
```

**Notes on the AI dependencies:**
- `easyocr` and `torch` are the heaviest installs (CV/OCR + CNN). On
  CPU-only machines the first EasyOCR call downloads model weights (~100MB)
  — make sure the machine has internet access on first run, or set the
  fallback path documented in `ai/ocr/extractor.py` to use `pytesseract`
  instead (`apt install tesseract-ocr`, `pip install pytesseract`).
- The bundled CNN classifier (`ai/models/cnn_classifier.py`) runs on an
  explainable heuristic fallback until you train it — no extra setup is
  required to get the full pipeline running end-to-end.

### 3. Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env             # VITE_API_BASE_URL=/api/v1
npm run dev
```

Visit http://localhost:5173. Vite proxies `/api` to `http://localhost:8000`
in dev (see `vite.config.ts`), so no CORS setup is needed locally.

### 4. Run the test suite

```bash
cd backend
pytest tests/
```

## Verifying the install

1. Open http://localhost:5173, register an account.
2. Go to **Analyze Screenshot**, upload any PNG/JPG (even a random photo
   works for a smoke test — OCR fields will simply come back empty).
3. Confirm a confidence score, verdict badge, and explainability checklist
   render.
4. Download the PDF report.
5. Log in as the admin account created above and open **Admin** to view
   users/logs.
