"""
Application entrypoint. Wires together FastAPI, CORS, rate limiting,
routers, static file serving for uploaded images, and startup table
creation (a lightweight alternative to running Alembic migrations for
local/dev use — production deployments should run `alembic upgrade head`
instead, see database/migrations/).
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.rate_limit import limiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Forensic analysis API for UPI payment screenshots. Uses OCR + classical computer-vision "
        "forensics + a placeholder CNN classifier to produce an explainable genuineness confidence "
        "score. This API does NOT connect to any bank or NPCI system and cannot confirm real "
        "transaction settlement — see the Future Scope section of the docs."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info("%s started. Environment=%s", settings.APP_NAME, settings.ENVIRONMENT)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
