"""
Writes structured events to the system_logs table for the Admin Dashboard.
"""
from sqlalchemy.orm import Session

from app.models.system_log import SystemLog


def log_event(db: Session, event_type: str, message: str, user_id: int | None = None,
              ip_address: str | None = None) -> None:
    entry = SystemLog(event_type=event_type, message=message, user_id=user_id, ip_address=ip_address)
    db.add(entry)
    db.commit()
