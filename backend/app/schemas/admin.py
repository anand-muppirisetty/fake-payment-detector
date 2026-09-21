"""Pydantic schemas for admin dashboard endpoints."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AdminUserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    total_analyses: int

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None


class SystemLogOut(BaseModel):
    id: int
    event_type: str
    message: str
    user_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_analyses: int
    suspicious_rate_percent: float
    analyses_last_7_days: int
