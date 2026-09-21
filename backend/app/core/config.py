"""
Centralized application configuration.

All values are loaded from environment variables (see backend/.env.example).
Using pydantic-settings gives us validated, typed configuration with sane
defaults for local development.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "AI-Powered Fake Payment Detection System"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- Security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql://fpd_user:fpd_password@localhost:5432/fake_payment_detector"
    )

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # --- File Upload ---
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 8
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg"]

    # --- Rate Limiting ---
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_UPLOAD: str = "10/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    # --- AI Analysis ---
    CONFIDENCE_GENUINE_THRESHOLD: int = 75   # >= this => "Likely Genuine"
    CONFIDENCE_SUSPICIOUS_THRESHOLD: int = 45  # below this => "Highly Suspicious"
    # Between the two thresholds => "Needs Manual Review"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor so we parse the environment only once."""
    return Settings()


settings = get_settings()
