# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Comment schemas
"""

from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """Schema cơ bản cho Comment"""
    content: str = Field(..., min_length=1, max_length=1000)
    images: Optional[List[str]] = []


class CommentCreate(CommentBase):
    """Schema tạo Comment mới"""
    parent_id: Optional[int] = None  # For reply to another comment


class CommentUpdate(BaseModel):
    """Schema cập nhật Comment"""
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(CommentBase):
    """Schema trả về Comment"""
    id: int
    report_id: int
    user_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed fields (optional)
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    replies_count: int = 0
    
    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Schema cho danh sách Comments"""
    comments: List[CommentResponse]
    total: int
