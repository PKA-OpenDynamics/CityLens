# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
User Service for MongoDB User Management
Handles CRUD operations for dashboard users
"""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import HTTPException, status

from app.schemas.user import (
    UserRegister, UserUpdate, UserInDB, UserBase,
    UserStatus, UserRole, UserApproval
)
from app.services.auth_service import auth_service


class UserService:
    """User management service for MongoDB"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
    
    async def create_user(self, user_data: UserRegister) -> dict:
        """Create new user with pending status"""
        # Check if email exists
        existing_user = await self.collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được đăng ký"
            )
        
        # Hash password
        hashed_password = auth_service.get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "phone": user_data.phone,
            "department": user_data.department,
            "position": user_data.position,
            "reason": user_data.reason,
            "role": UserRole.VIEWER,  # Default role
            "status": UserStatus.PENDING,  # Waiting for approval
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "approved_by": None,
            "approved_at": None,
            "rejection_reason": None,
            "avatar_url": None
        }
        
        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        
        return user_doc
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not auth_service.verify_password(password, user["hashed_password"]):
            return None
        
        # Check user status
        auth_service.validate_user_status(user["status"])
        
        # Update last login
        await self.collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return user
    
    async def update_user_profile(self, user_id: str, update_data: UserUpdate) -> dict:
        """Update user profile information"""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID không hợp lệ"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        return await self.get_user_by_id(user_id)
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        # Verify old password
        if not auth_service.verify_password(old_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu cũ không đúng"
            )
        
        # Hash new password
        hashed_password = auth_service.get_password_hash(new_password)
        
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return True
    
    async def approve_user(
        self,
        user_id: str,
        approval_data: UserApproval,
        admin_id: str
    ) -> dict:
        """Approve or reject user registration"""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID không hợp lệ"
            )
        
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        if user["status"] != UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User không ở trạng thái chờ duyệt"
            )
        
        update_data = {
            "status": approval_data.status,
            "approved_by": admin_id,
            "approved_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if approval_data.status == "approved":
            update_data["role"] = approval_data.role or UserRole.VIEWER
        elif approval_data.status == "rejected":
            update_data["rejection_reason"] = approval_data.rejection_reason
        
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return await self.get_user_by_id(user_id)
    
    async def get_pending_users(self, skip: int = 0, limit: int = 50) -> List[dict]:
        """Get all pending users for admin approval"""
        cursor = self.collection.find(
            {"status": UserStatus.PENDING}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        users = await cursor.to_list(length=limit)
        
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    
    async def get_all_users(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[dict]:
        """Get all users with optional filters"""
        query = {}
        
        if status:
            query["status"] = status
        if role:
            query["role"] = role
        
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        users = await cursor.to_list(length=limit)
        
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    
    async def count_users(self, status: Optional[str] = None) -> int:
        """Count users by status"""
        query = {}
        if status:
            query["status"] = status
        
        return await self.collection.count_documents(query)
    
    async def update_user_role(self, user_id: str, new_role: str, admin_id: str) -> dict:
        """Update user role (admin only)"""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID không hợp lệ"
            )
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "role": new_role,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        return await self.get_user_by_id(user_id)
    
    async def suspend_user(self, user_id: str, admin_id: str) -> dict:
        """Suspend user account"""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID không hợp lệ"
            )
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "status": UserStatus.SUSPENDED,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        return await self.get_user_by_id(user_id)
