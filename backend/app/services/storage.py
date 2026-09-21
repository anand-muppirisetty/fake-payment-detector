"""
Local file storage service — saves uploaded screenshots under a UUID-based
filename (never trusting the user-supplied filename) and enforces size /
extension validation.
"""
from __future__ import annotations

import hashlib
import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def _ensure_upload_dir() -> str:
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.UPLOAD_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def validate_upload(file: UploadFile, content: bytes) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}",
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )
    # Minimal magic-byte sanity check (defense in depth beyond extension check)
    if not (content.startswith(b"\xff\xd8") or content.startswith(b"\x89PNG")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not look like a valid PNG/JPEG image.",
        )


def save_upload(file: UploadFile, content: bytes) -> tuple[str, str, str]:
    """
    Persist the validated file to disk under a UUID name.
    Returns (stored_filename, absolute_path, sha256_hash).
    """
    upload_dir = _ensure_upload_dir()
    ext = os.path.splitext(file.filename or "")[1].lower()
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(upload_dir, stored_filename)
    with open(abs_path, "wb") as f:
        f.write(content)
    file_hash = hashlib.sha256(content).hexdigest()
    return stored_filename, abs_path, file_hash


def get_upload_path(stored_filename: str) -> str:
    upload_dir = _ensure_upload_dir()
    path = os.path.join(upload_dir, stored_filename)
    if not os.path.abspath(path).startswith(os.path.abspath(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path.")
    return path
