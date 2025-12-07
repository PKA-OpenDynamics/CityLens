# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API Dependencies
FastAPI dependency injection utilities
"""

from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.db.postgres import SessionLocal
from app.core.config import settings

security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token
    Returns user dict or None for now (stub implementation)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Simple stub - return a dict with user info
        # In production, query the database for the actual user
        return {"id": user_id, "email": payload.get("email", ""), "role": "citizen"}
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Ensure user is active
    """
    return current_user


def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """
    Ensure user is admin or moderator
    """
    if current_user.get("role") not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
