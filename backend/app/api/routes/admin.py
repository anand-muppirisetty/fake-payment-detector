"""
Admin-only routes: user management, system-wide analysis statistics, logs.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.analysis import Analysis, VerdictLabel
from app.models.system_log import SystemLog
from app.models.user import User, UserRole
from app.schemas.admin import AdminStats, AdminUserOut, AdminUserUpdate, SystemLogOut
from app.services.logging_service import log_event

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@router.get("/users", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    out = []
    for u in users:
        count = db.query(func.count(Analysis.id)).filter(Analysis.owner_id == u.id).scalar()
        out.append(AdminUserOut(
            id=u.id, full_name=u.full_name, email=u.email, role=u.role.value,
            is_active=u.is_active, created_at=u.created_at, total_analyses=count or 0,
        ))
    return out


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(user_id: int, payload: AdminUserUpdate, db: Session = Depends(get_db),
                 admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        if payload.role not in (UserRole.USER.value, UserRole.ADMIN.value):
            raise HTTPException(status_code=400, detail="Invalid role.")
        user.role = UserRole(payload.role)
    db.commit()
    db.refresh(user)
    log_event(db, "ADMIN_ACTION", f"Admin {admin.email} updated user {user.email} "
                                    f"(active={user.is_active}, role={user.role.value})", user_id=admin.id)
    count = db.query(func.count(Analysis.id)).filter(Analysis.owner_id == user.id).scalar()
    return AdminUserOut(id=user.id, full_name=user.full_name, email=user.email, role=user.role.value,
                         is_active=user.is_active, created_at=user.created_at, total_analyses=count or 0)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own admin account.")
    db.delete(user)
    db.commit()
    log_event(db, "ADMIN_ACTION", f"Admin {admin.email} deleted user {user.email}", user_id=admin.id)
    return None


@router.get("/stats", response_model=AdminStats)
def admin_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0
    total_analyses = db.query(func.count(Analysis.id)).scalar() or 0
    suspicious = db.query(func.count(Analysis.id)).filter(
        Analysis.verdict == VerdictLabel.HIGHLY_SUSPICIOUS
    ).scalar() or 0
    last_7 = db.query(func.count(Analysis.id)).filter(
        Analysis.created_at >= datetime.utcnow() - timedelta(days=7)
    ).scalar() or 0
    rate = round((suspicious / total_analyses) * 100, 1) if total_analyses else 0.0
    return AdminStats(
        total_users=total_users, active_users=active_users, total_analyses=total_analyses,
        suspicious_rate_percent=rate, analyses_last_7_days=last_7,
    )


@router.get("/logs", response_model=list[SystemLogOut])
def get_logs(db: Session = Depends(get_db), limit: int = Query(200, le=1000),
             event_type: str | None = None):
    q = db.query(SystemLog)
    if event_type:
        q = q.filter(SystemLog.event_type == event_type)
    return q.order_by(SystemLog.created_at.desc()).limit(limit).all()
