"""Aggregates all v1 API routers under a single prefix."""
from fastapi import APIRouter

from app.api.routes import admin, analysis, auth

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(analysis.router)
api_router.include_router(admin.router)
