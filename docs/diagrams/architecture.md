# System Architecture Diagram

```mermaid
flowchart TB
    subgraph Client["Frontend — React + TypeScript + Tailwind"]
        UI1[Landing / Auth Pages]
        UI2[Dashboard]
        UI3[Upload]
        UI4[History]
        UI5[Admin]
    end

    subgraph API["Backend — FastAPI"]
        AUTH[Auth Routes<br/>JWT + bcrypt]
        AN[Analysis Routes<br/>upload / history / stats]
        ADM[Admin Routes]
        MW[Middleware<br/>CORS · Rate Limit · Validation]
    end

    subgraph AIPipe["AI Pipeline"]
        OCR[OCR Extractor<br/>EasyOCR / Tesseract]
        FOR[Forensic Analyzer<br/>OpenCV checks]
        CNN[CNN Classifier<br/>placeholder architecture]
        CONF[Confidence Scoring<br/>rule-based aggregation]
    end

    subgraph Storage["Storage & Persistence"]
        FS[(Local Disk<br/>UUID-named uploads)]
        DB[(PostgreSQL<br/>users / analyses / logs)]
    end

    UI1 & UI2 & UI3 & UI4 & UI5 -->|REST + JWT| MW
    MW --> AUTH
    MW --> AN
    MW --> ADM

    AN -->|save file| FS
    AN -->|run pipeline| OCR
    OCR --> FOR
    FOR --> CNN
    CNN --> CONF
    CONF -->|persist result| DB
    AUTH --> DB
    ADM --> DB
    AN -->|read/write| DB
```

## Layer responsibilities

- **Frontend** — SPA rendering all 14 feature areas; talks to the backend
  exclusively via the versioned REST API (`/api/v1`).
- **Backend** — FastAPI app handling auth, request validation, rate
  limiting, and orchestration; contains no AI logic itself, only calls into
  the `ai/` package.
- **AI Pipeline** — pure Python package (`ai/`), independent of FastAPI, so
  it can be unit-tested or reused (e.g. in a batch job) without spinning up
  the API.
- **Storage** — uploaded screenshots on local disk under UUID filenames;
  structured results, users, and audit logs in PostgreSQL.
