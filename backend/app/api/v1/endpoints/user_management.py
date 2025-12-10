# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User Management API Endpoints
Full CRUD for Web Dashboard and Mobile App users
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.db.postgres import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service as web_auth_service, get_password_hash

router = APIRouter()


class UserCreate(BaseModel):
    """Schema for creating new user"""
    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None
    password: str
    role: UserRole = UserRole.CITIZEN
    source: str = 'dashboard'  # 'dashboard' or 'app'
    department: Optional[str] = None
    position: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: str
    source: str
    is_active: bool
    is_verified: bool
    reports_count: int
    points: int
    level: int
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total: int
    dashboard: int
    app: int
    active: int
    inactive: int
    by_role: dict


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all users with filtering
    
    - **role**: Filter by user role
    - **source**: Filter by source ('dashboard' or 'app')
    - **is_active**: Filter by active status
    - **search**: Search in email, username, full_name
    """
    query = db.query(User)

    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if source:
        # Assuming source is stored in properties JSONB
        query = query.filter(User.properties['source'].astext == source)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_pattern)) |
            (User.username.ilike(search_pattern)) |
            (User.full_name.ilike(search_pattern))
        )

    # Order by created_at desc
    query = query.order_by(User.created_at.desc())
    
    users = query.offset(skip).limit(limit).all()
    
    # Add source from properties
    result = []
    for user in users:
        user_dict = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'full_name': user.full_name or user.username,
            'phone': user.phone,
            'role': user.role.value,
            'source': user.properties.get('source', 'app') if user.properties else 'app',
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'reports_count': user.reports_count,
            'points': user.points,
            'level': user.level,
            'created_at': user.created_at,
            'last_login': user.last_login,
        }
        result.append(UserResponse(**user_dict))
    
    return result


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(db: Session = Depends(get_db)):
    """Get user statistics"""
    total = db.query(func.count(User.id)).scalar()
    
    # Count by source
    dashboard_count = db.query(func.count(User.id)).filter(
        User.properties['source'].astext == 'dashboard'
    ).scalar() or 0
    
    app_count = total - dashboard_count
    
    # Count by status
    active = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    inactive = total - active
    
    # Count by role
    by_role = {}
    for role in UserRole:
        count = db.query(func.count(User.id)).filter(User.role == role).scalar()
        by_role[role.value] = count
    
    return UserStatsResponse(
        total=total,
        dashboard=dashboard_count,
        app=app_count,
        active=active,
        inactive=inactive,
        by_role=by_role
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc tên đăng nhập đã tồn tại"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=True,
        is_verified=True if user_data.source == 'dashboard' else False,
        properties={
            'source': user_data.source,
            'department': user_data.department,
            'position': user_data.position,
        }
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        username=db_user.username,
        full_name=db_user.full_name,
        phone=db_user.phone,
        role=db_user.role.value,
        source=user_data.source,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        reports_count=db_user.reports_count,
        points=db_user.points,
        level=db_user.level,
        created_at=db_user.created_at,
        last_login=db_user.last_login,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.value,
        source=user.properties.get('source', 'app') if user.properties else 'app',
        is_active=user.is_active,
        is_verified=user.is_verified,
        reports_count=user.reports_count,
        points=user.points,
        level=user.level,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    # Update fields
    if user_data.email is not None:
        # Check email uniqueness
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng"
            )
        user.email = user_data.email
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.phone is not None:
        user.phone = user_data.phone
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # Update properties
    if user_data.department is not None or user_data.position is not None:
        if not user.properties:
            user.properties = {}
        if user_data.department is not None:
            user.properties['department'] = user_data.department
        if user_data.position is not None:
            user.properties['position'] = user_data.position
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.value,
        source=user.properties.get('source', 'app') if user.properties else 'app',
        is_active=user.is_active,
        is_verified=user.is_verified,
        reports_count=user.reports_count,
        points=user.points,
        level=user.level,
        created_at=user.created_at,
        last_login=user.last_login,
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Delete user (soft delete by setting is_active to False)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    # Soft delete
    user.is_active = False
    db.commit()
    
    return {"success": True, "message": "Đã xóa người dùng"}


@router.put("/{user_id}/toggle-status")
async def toggle_user_status(user_id: str, db: Session = Depends(get_db)):
    """Toggle user active status"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {
        "success": True,
        "message": f"Đã {'mở khóa' if user.is_active else 'khóa'} tài khoản",
        "is_active": user.is_active
    }
