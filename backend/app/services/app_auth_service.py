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

# Password hashing context - lazy initialization to avoid bcrypt 72-byte limit error
_pwd_context = None

def get_pwd_context():
    """Get password context with lazy initialization"""
    global _pwd_context
    if _pwd_context is None:
        try:
            _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        except (ValueError, AttributeError) as e:
            # If initialization fails due to bcrypt bug detection or version issues,
            # return None and we'll use bcrypt directly as fallback
            print(f"Warning: Passlib initialization failed: {e}")
            print("Falling back to bcrypt direct")
            _pwd_context = None
    return _pwd_context

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
        pwd_context = get_pwd_context()
        if pwd_context:
            try:
                return pwd_context.hash(password)
            except Exception:
                pass
        
        # Fallback to bcrypt direct
        import bcrypt
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hashed password"""
        pwd_context = get_pwd_context()
        if pwd_context:
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                pass
        
        # Fallback to bcrypt direct
        import bcrypt
        try:
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
            hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
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
