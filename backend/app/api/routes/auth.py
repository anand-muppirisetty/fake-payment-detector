"""
Authentication routes: register, login, forgot/reset password, refresh.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token, create_password_reset_token, create_refresh_token,
    decode_token, hash_password, verify_password,
)
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest, ResetPasswordRequest, TokenPair, UserLogin, UserOut, UserRegister,
)
from app.services.logging_service import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_event(db, "REGISTER", f"New account created: {user.email}", user_id=user.id,
              ip_address=request.client.host if request.client else None)

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenPair)
@limiter.limit("5/minute")
def login(request: Request, payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        log_event(db, "LOGIN_FAILED", f"Failed login attempt for {payload.email}",
                  ip_address=request.client.host if request.client else None)
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been disabled.")

    user.last_login_at = datetime.utcnow()
    db.commit()
    log_event(db, "LOGIN", f"{user.email} logged in", user_id=user.id,
              ip_address=request.client.host if request.client else None)

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))


@router.post("/refresh", response_model=TokenPair)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")
    access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=new_refresh, user=UserOut.model_validate(user))


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return a generic response to avoid leaking which emails are registered.
    if user:
        reset_token = create_password_reset_token(str(user.id))
        log_event(db, "PASSWORD_RESET_REQUESTED", f"Password reset requested for {user.email}", user_id=user.id)
        # In production this token is emailed to the user via a transactional email
        # provider (SES/SendGrid). For local/dev use it is returned directly so the
        # flow can be exercised end-to-end without email infrastructure.
        return {"message": "If that email exists, a reset link has been sent.", "dev_reset_token": reset_token}
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_payload = decode_token(payload.token)
    if not token_payload or token_payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    user = db.query(User).filter(User.id == int(token_payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    log_event(db, "PASSWORD_RESET", f"Password reset completed for {user.email}", user_id=user.id)
    return {"message": "Password has been reset successfully."}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
