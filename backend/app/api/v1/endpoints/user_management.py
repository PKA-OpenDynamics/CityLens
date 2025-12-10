# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User Management API Endpoints
Full CRUD for Web Dashboard and Mobile App users
- Web Dashboard users: MongoDB Docker (collection: users)
- Mobile App users: MongoDB Atlas (collection: user_profile)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from bson import ObjectId

from app.db.mongodb import get_mongodb
from app.db.mongodb_atlas import get_mongodb_atlas
from app.services.auth_service import auth_service as web_auth_service
from app.services.app_auth_service import AppAuthService

router = APIRouter()


class UserCreate(BaseModel):
    """Schema for creating new user"""
    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None
    password: str
    role: str = 'citizen'  # 'admin', 'staff', 'viewer', 'citizen'
    source: str = 'dashboard'  # 'dashboard' or 'app'
    department: Optional[str] = None
    position: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    username: str
    full_name: str
    phone: Optional[str] = None
    role: str
    source: str
    is_active: bool
    is_verified: bool
    reports_count: int = 0
    points: int = 0
    level: int = 1
    created_at: datetime
    last_login: Optional[datetime] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None

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


def normalize_dashboard_user(user: dict) -> UserResponse:
    """Convert MongoDB Docker user to UserResponse"""
    return UserResponse(
        id=str(user.get('_id', '')),
        email=user.get('email', ''),
        username=user.get('email', '').split('@')[0],  # Dashboard users may not have username
        full_name=user.get('full_name', ''),
        phone=user.get('phone'),
        role=user.get('role', 'viewer'),
        source='dashboard',
        is_active=user.get('status') in ['approved', 'active'],
        is_verified=user.get('status') == 'approved',
        reports_count=0,
        points=0,
        level=1,
        created_at=user.get('created_at', datetime.utcnow()),
        last_login=user.get('last_login'),
        department=user.get('department'),
        position=user.get('position'),
        status=user.get('status', 'pending')
    )


def normalize_app_user(user: dict) -> UserResponse:
    """Convert MongoDB Atlas user to UserResponse"""
    return UserResponse(
        id=str(user.get('_id', '')),
        email=user.get('email', ''),
        username=user.get('username', user.get('email', '').split('@')[0]),
        full_name=user.get('full_name', user.get('fullName', '')),
        phone=user.get('phone'),
        role=user.get('role', 'citizen'),
        source='app',
        is_active=user.get('is_active', True),
        is_verified=user.get('is_verified', user.get('emailVerified', False)),
        reports_count=user.get('reports_count', user.get('reportsCount', 0)),
        points=user.get('points', 0),
        level=user.get('level', 1),
        created_at=user.get('created_at', user.get('createdAt', datetime.utcnow())),
        last_login=user.get('last_login', user.get('lastLogin')),
        department=None,
        position=None,
        status='active' if user.get('is_active', True) else 'inactive'
    )


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    role: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """
    Get all users from both sources with filtering
    
    - **role**: Filter by user role
    - **source**: Filter by source ('dashboard' or 'app')
    - **is_active**: Filter by active status
    - **search**: Search in email, username, full_name
    """
    result = []
    
    # Build query filters
    dashboard_query = {}
    app_query = {}
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        dashboard_query["$or"] = [
            {"email": search_regex},
            {"full_name": search_regex}
        ]
        app_query["$or"] = [
            {"email": search_regex},
            {"username": search_regex},
            {"full_name": search_regex},
            {"fullName": search_regex}
        ]
    
    if role:
        dashboard_query["role"] = role
        app_query["role"] = role
    
    if is_active is not None:
        if is_active:
            dashboard_query["status"] = {"$in": ["approved", "active"]}
            app_query["is_active"] = True
        else:
            dashboard_query["status"] = {"$in": ["pending", "rejected", "suspended", "inactive"]}
            app_query["is_active"] = False
    
    # Get Dashboard users from MongoDB Docker
    if source is None or source == 'dashboard':
        try:
            dashboard_users = await db.users.find(dashboard_query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
            for user in dashboard_users:
                result.append(normalize_dashboard_user(user))
        except Exception as e:
            print(f"Error fetching dashboard users: {e}")
    
    # Get App users from MongoDB Atlas
    if source is None or source == 'app':
        try:
            app_users = await atlas_db.user_profile.find(app_query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
            for user in app_users:
                result.append(normalize_app_user(user))
        except Exception as e:
            print(f"Error fetching app users: {e}")
    
    # Sort combined result by created_at
    result.sort(key=lambda x: x.created_at, reverse=True)
    
    return result[:limit]


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Get user statistics from both sources"""
    
    # Dashboard users stats (MongoDB Docker)
    dashboard_total = 0
    dashboard_active = 0
    dashboard_by_role = {"admin": 0, "staff": 0, "viewer": 0}
    
    try:
        dashboard_total = await db.users.count_documents({})
        dashboard_active = await db.users.count_documents({"status": {"$in": ["approved", "active"]}})
        
        # Count by role
        for role in ["admin", "staff", "viewer"]:
            count = await db.users.count_documents({"role": role})
            dashboard_by_role[role] = count
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
    
    # App users stats (MongoDB Atlas)
    app_total = 0
    app_active = 0
    app_by_role = {"citizen": 0}
    
    try:
        app_total = await atlas_db.user_profile.count_documents({})
        app_active = await atlas_db.user_profile.count_documents({"is_active": True})
        
        # App users are typically citizens
        app_by_role["citizen"] = app_total
    except Exception as e:
        print(f"Error fetching app stats: {e}")
    
    # Combine stats
    total = dashboard_total + app_total
    active = dashboard_active + app_active
    inactive = total - active
    
    by_role = {**dashboard_by_role, **app_by_role}
    
    return UserStatsResponse(
        total=total,
        dashboard=dashboard_total,
        app=app_total,
        active=active,
        inactive=inactive,
        by_role=by_role
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Create a new user in the appropriate database"""
    
    if user_data.source == 'dashboard':
        # Create in MongoDB Docker
        existing = await db.users.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký"
            )
        
        hashed_password = web_auth_service.get_password_hash(user_data.password)
        
        user_doc = {
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "department": user_data.department,
            "position": user_data.position,
            "role": user_data.role,
            "status": "approved",  # Admin-created users are auto-approved
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
        }
        
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return normalize_dashboard_user(user_doc)
    
    else:
        # Create in MongoDB Atlas
        existing = await atlas_db.user_profile.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký"
            )
        
        auth_service = AppAuthService(atlas_db)
        hashed_password = auth_service.hash_password(user_data.password)
        
        user_doc = {
            "email": user_data.email,
            "username": user_data.username,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "role": "citizen",
            "is_active": True,
            "is_verified": True,
            "reports_count": 0,
            "points": 0,
            "level": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await atlas_db.user_profile.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return normalize_app_user(user_doc)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    source: str = Query('dashboard', description="User source: 'dashboard' or 'app'"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Get user by ID from specified source"""
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID không hợp lệ"
        )
    
    if source == 'dashboard':
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        return normalize_dashboard_user(user)
    else:
        user = await atlas_db.user_profile.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        return normalize_app_user(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    source: str = Query('dashboard', description="User source: 'dashboard' or 'app'"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Update user information"""
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID không hợp lệ"
        )
    
    update_dict = user_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    # Convert is_active to status for dashboard users
    if source == 'dashboard' and 'is_active' in update_dict:
        is_active = update_dict.pop('is_active')
        update_dict['status'] = 'approved' if is_active else 'suspended'
    
    if source == 'dashboard':
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return normalize_dashboard_user(user)
    else:
        result = await atlas_db.user_profile.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        user = await atlas_db.user_profile.find_one({"_id": ObjectId(user_id)})
        return normalize_app_user(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    source: str = Query('dashboard', description="User source: 'dashboard' or 'app'"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Delete user (soft delete by setting status/is_active)"""
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID không hợp lệ"
        )
    
    if source == 'dashboard':
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"status": "suspended", "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    else:
        result = await atlas_db.user_profile.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    return {"success": True, "message": "Đã xóa người dùng"}


@router.put("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    source: str = Query('dashboard', description="User source: 'dashboard' or 'app'"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    atlas_db: AsyncIOMotorDatabase = Depends(get_mongodb_atlas)
):
    """Toggle user active status"""
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID không hợp lệ"
        )
    
    if source == 'dashboard':
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        current_status = user.get('status', 'pending')
        new_status = 'suspended' if current_status in ['approved', 'active'] else 'approved'
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
        
        is_active = new_status in ['approved', 'active']
    else:
        user = await atlas_db.user_profile.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        is_active = not user.get('is_active', True)
        
        await atlas_db.user_profile.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": is_active, "updated_at": datetime.utcnow()}}
        )
    
    return {
        "success": True,
        "message": f"Đã {'mở khóa' if is_active else 'khóa'} tài khoản",
        "is_active": is_active
    }
