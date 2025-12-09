# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App Authentication Service
Handles JWT tokens and password hashing for mobile app users
Uses MongoDB Atlas (cloud)
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.schemas.app_user import AppUserInDB, AppUserProfile

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration for Mobile App
JWT_SECRET = settings.SECRET_KEY
JWT_ALGORITHM = settings.ALGORITHM
JWT_EXPIRES_IN = "7d"  # 7 days for mobile app


class AppAuthService:
    """Authentication service for mobile app users"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.user_profile
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hashed password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: str, username: str) -> str:
        """Create JWT access token for mobile app"""
        expires_delta = timedelta(days=7)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "userId": user_id,
            "username": username,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "mobile_app"
        }
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )
    
    async def register_user(self, username: str, email: str, password: str, 
                           full_name: str, phone: Optional[str] = None) -> AppUserProfile:
        """Register new mobile app user"""
        # Check if username or email exists
        existing = await self.collection.find_one({
            "$or": [{"username": username}, {"email": email}]
        })
        
        if existing:
            if existing.get("username") == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tên đăng nhập đã tồn tại"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email đã được sử dụng"
                )
        
        # Create user document (matching web-app/server structure)
        user_doc = {
            "_id": ObjectId(),
            "username": username,
            "email": email,
            "password": self.hash_password(password),
            "full_name": full_name,
            "phone": phone or "",
            "is_active": True,
            "role": "user",
            "level": 1,
            "points": 0,
            "reputation_score": 0,
            "is_verified": False,
            "is_admin": False,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "updated_at": datetime.utcnow(),
        }
        
        await self.collection.insert_one(user_doc)
        
        # Return user without password
        user_doc.pop("password")
        user_doc["_id"] = str(user_doc["_id"])
        
        return AppUserProfile(**user_doc)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[AppUserInDB]:
        """Authenticate mobile app user"""
        user = await self.collection.find_one({"username": username})
        
        if not user:
            return None
        
        if not self.verify_password(password, user["password"]):
            return None
        
        # Update last login
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        user["_id"] = str(user["_id"])
        return AppUserInDB(**user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[AppUserProfile]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None
        
        user = await self.collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            return None
        
        user.pop("password", None)
        user["_id"] = str(user["_id"])
        
        return AppUserProfile(**user)
    
    async def update_user_profile(self, user_id: str, update_data: dict) -> AppUserProfile:
        """Update user profile"""
        if not ObjectId.is_valid(user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID không hợp lệ"
            )
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy user"
            )
        
        return await self.get_user_by_id(user_id)
