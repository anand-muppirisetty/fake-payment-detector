# Database ER Diagram

```mermaid
erDiagram
    USERS ||--o{ ANALYSES : owns
    USERS ||--o{ SYSTEM_LOGS : triggers

    USERS {
        int id PK
        string full_name
        string email UK
        string hashed_password
        enum role "user | admin"
        bool is_active
        datetime created_at
        datetime last_login_at
    }

    ANALYSES {
        int id PK
        int owner_id FK
        string stored_filename "UUID-based"
        string original_filename
        int file_size_bytes
        string file_hash_sha256
        string ocr_amount
        string ocr_date
        string ocr_time
        string ocr_utr
        string ocr_bank_name
        string ocr_sender_upi
        string ocr_receiver_upi
        string ocr_payment_status
        text ocr_raw_text
        json forensic_findings
        int forensic_flags_count
        float confidence_score
        enum verdict "Likely Genuine | Needs Manual Review | Highly Suspicious"
        bool is_suspicious
        json explanation_reasons
        datetime created_at
    }

    SYSTEM_LOGS {
        int id PK
        string event_type
        text message
        int user_id FK "nullable"
        string ip_address
        datetime created_at
    }
```

## Notes

- `analyses.forensic_findings` and `analyses.explanation_reasons` are
  stored as `JSON` columns rather than normalized child tables — each
  analysis owns a small, fixed-shape list that is always read/written
  together with its parent row, so JSON keeps the schema simple without
  sacrificing queryability of the top-level fields (`confidence_score`,
  `verdict`, etc.) used for dashboard aggregation.
- `file_hash_sha256` is indexed to support future de-duplication /
  integrity-check features.
- `system_logs.user_id` is nullable to allow logging pre-auth events (e.g.
  failed login attempts against an email with no matching account).
