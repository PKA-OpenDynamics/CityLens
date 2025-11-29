# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user(
    db: Session = Depends(get_db),
    # TODO: Add current_user dependency
):
    """Lấy thông tin người dùng hiện tại"""
    # Placeholder - cần implement authentication dependency
    return {"message": "Endpoint chưa hoàn thiện"}


@router.put("/me", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    # TODO: Add current_user dependency
):
    """Cập nhật thông tin người dùng"""
    # Placeholder - cần implement authentication dependency
    return {"message": "Endpoint chưa hoàn thiện"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Lấy thông tin người dùng theo ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    return user
