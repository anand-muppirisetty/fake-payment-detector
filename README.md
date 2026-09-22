<div align="center">

<img width="100%" alt="banner" src="https://capsule-render.vercel.app/api?type=waving&color=0:33d6c0,100:0c1220&height=200&section=header&text=Fake%20Payment%20Detector%20AI&fontSize=42&fontColor=ffffff&fontAlignY=38&desc=Forensic%20AI%20for%20UPI%20Payment%20Screenshots&descAlignY=58&descSize=18" />

### 🔍 AI-Powered Forensic Analysis for UPI Payment Screenshots
**OCR · Computer Vision · Explainable Confidence Scoring**

*A final-year B.Tech AI & ML project — detects edited/fake payment screenshots without ever touching real bank data.*

<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styling-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-CNN-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)

<br/>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/anand-kumar-muppirisetty-884a59315)
[![Gmail](https://img.shields.io/badge/Gmail-Contact_Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:anandkumar.muppirisetty@gmail.com)

</div>

<br/>

## 📖 Table of Contents

- [⚠️ Scope & Disclaimer](#️-scope--disclaimer)
- [✨ Features](#-features)
- [🖥️ Tech Stack](#️-tech-stack)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [📚 Documentation](#-documentation)
- [🔮 Future Scope](#-future-scope)
- [👨‍💻 Author](#-author)

---

## ⚠️ Scope & Disclaimer

> **This project does not verify real bank transactions.**

It performs **forensic image analysis** of an uploaded screenshot — OCR text
extraction plus classical computer-vision and CNN-based manipulation detection —
to produce an explainable confidence score describing how likely the **image**
is to have been digitally edited.

It never contacts a bank, UPI switch, or NPCI system, has no access to real
account/transaction data, and its verdict should not be treated as legal or
financial proof. Real transaction verification requires regulated institutional
API access — intentionally out of scope for this academic project.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🏠 Landing Page
Hero section, feature cards, architecture diagram, About the AI, Future Scope

### 🔐 Authentication
Register, login, forgot/reset password — JWT access + refresh tokens

### 📊 Dashboard
Total analyses, suspicious/genuine counts, average confidence, pie chart, bar chart, timeline

### 📤 Smart Upload
Drag-and-drop PNG/JPG/JPEG with live preview

### 🔤 OCR Engine
Extracts amount, date, time, UTR, bank name, sender/receiver UPI ID, payment status

### 🕵️ AI Forensic Analysis
9 independent checks: font inconsistency, copy-paste artifacts, compression
artifacts, edited amount, fake QR, metadata anomalies, cropping, blur
inconsistency, + CNN signal

</td>
<td width="50%">

### 🎯 Confidence Score
0–100% score with a 3-tier verdict: **Likely Genuine** / **Needs Manual Review** / **Highly Suspicious**

### 💡 Explainability
Plain-language checklist of exactly *why* a screenshot was flagged

### 🕘 History
Search, sort, filter, delete past analyses

### 📄 Export Report
Downloadable PDF with screenshot, extracted text, findings, and score

### 🛡️ Admin Dashboard
User management, system-wide stats, audit logs

### 📚 API Docs
Auto-generated Swagger UI at `/api/docs`

</td>
</tr>
</table>

---

## 🖥️ Tech Stack

<div align="center">

| Layer | Technology |
|:---:|:---|
| **Frontend** | React · TypeScript · Tailwind CSS · Framer Motion · Recharts |
| **Backend** | Python · FastAPI · JWT Auth · SlowAPI Rate Limiting |
| **AI Pipeline** | EasyOCR / Tesseract · OpenCV · scikit-image · PyTorch (CNN) |
| **Database** | PostgreSQL · SQLAlchemy · Alembic |
| **Storage** | Local disk · UUID-named files |
| **DevOps** | Docker · Docker Compose |

</div>

---

## 🏗️ Architecture

```mermaid
flowchart LR
    A[📤 Upload Screenshot] --> B[🔤 OCR Extraction]
    B --> C[🕵️ Forensic CV Checks]
    C --> D[🧠 CNN Signal]
    D --> E[🎯 Confidence Scoring]
    E --> F[(🗄️ PostgreSQL)]
    F --> G[📊 Dashboard / History / PDF Report]
```

Full diagrams: [Architecture](docs/diagrams/architecture.md) · [ER Diagram](docs/diagrams/er-diagram.md) · [Sequence Diagram](docs/diagrams/sequence-diagram.md)

---

## 🚀 Quick Start

```bash
git clone https://github.com/<your-username>/fake-payment-detector.git
cd fake-payment-detector
docker compose up --build
```

| Service | URL |
|---|---|
| 🌐 Frontend | http://localhost:5173 |
| ⚙️ Backend + Swagger Docs | http://localhost:8000/api/docs |

Create your first admin account:
```bash
docker compose exec backend python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
```

📖 Full setup guide (with or without Docker): [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

---

## 📁 Project Structure
