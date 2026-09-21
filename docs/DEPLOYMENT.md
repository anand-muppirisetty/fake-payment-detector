# Deployment Guide

This guide covers taking Fake Payment Detector AI from local development to a small
production/demo deployment (e.g. a single VPS, or separate managed
services). It assumes familiarity with the local setup in
[`INSTALLATION.md`](INSTALLATION.md).

## 1. Environment configuration

Set real values for (never commit these):

```
SECRET_KEY=<long random string, e.g. `openssl rand -hex 32`>
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<db>
CORS_ORIGINS=["https://your-frontend-domain.com"]
ENVIRONMENT=production
DEBUG=false
```

## 2. Database

- Use a managed PostgreSQL instance (RDS, Cloud SQL, Supabase, etc.) or a
  hardened self-hosted instance.
- Run schema migrations instead of relying on `create_all()`:
  ```bash
  cd backend
  alembic revision --autogenerate -m "initial schema"
  alembic upgrade head
  ```
- Create the first admin via `scripts/create_admin.py` (run once, then
  remove/rotate the credentials used).

## 3. Backend deployment

**Option A — container (recommended):**
```bash
docker build -t screenscan-backend ./backend
docker run -d --env-file backend/.env -p 8000:8000 \
  -v screenscan_uploads:/app/uploads screenscan-backend
```
Put this behind a reverse proxy (Nginx/Caddy) that terminates TLS and
forwards to port 8000. Run with multiple Uvicorn workers behind the proxy
for concurrency:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option B — PaaS** (Render, Railway, Fly.io, etc.): point the build at
`backend/`, set the start command to the Uvicorn line above, and attach a
persistent volume for `backend/uploads` (screenshots must survive
restarts) plus the managed Postgres add-on.

## 4. Frontend deployment

Build a static bundle and serve it from any static host / CDN:
```bash
cd frontend
npm run build      # outputs to frontend/dist
```
Deploy `dist/` to Vercel, Netlify, S3+CloudFront, or Nginx. Set
`VITE_API_BASE_URL` at build time to the backend's public URL (e.g.
`https://api.your-domain.com/api/v1`) since Vite's dev proxy does not apply
to static builds.

## 5. Reverse proxy / TLS

Example Nginx snippet routing both services behind one domain:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        root /var/www/screenscan-frontend/dist;
        try_files $uri /index.html;
    }
}
```

## 6. File storage at scale

The default local-disk + UUID-filename storage (`backend/app/services/storage.py`)
works well for a single-server deployment. For multi-instance deployments,
swap it for an object store (S3-compatible) behind the same
`save_upload()` / `get_upload_path()` interface so the rest of the app is
unaffected.

## 7. Operational checklist

- [ ] `SECRET_KEY` is a long random value, not the default
- [ ] `DEBUG=false` in production
- [ ] `CORS_ORIGINS` restricted to your real frontend domain(s)
- [ ] Postgres backups scheduled
- [ ] `backend/uploads` volume backed up or migrated to object storage
- [ ] Rate limits reviewed for expected traffic (`app/core/config.py`)
- [ ] HTTPS enforced end-to-end
- [ ] Admin account credentials rotated after initial setup
- [ ] Swagger UI (`/api/docs`) access reviewed — consider disabling in
      production if the API shouldn't be publicly browsable
