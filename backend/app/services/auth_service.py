# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Authentication Service for User Management
Handles JWT tokens, password hashing, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.user import TokenData, UserRole, UserStatus

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


class AuthService:
    """Authentication and authorization service"""
    
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
    def get_password_hash(password: str) -> str:
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
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token (valid for 30 days)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> TokenData:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            return TokenData(email=email, user_id=user_id, role=role)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc đã hết hạn"
            )
    
    @staticmethod
    def validate_user_status(status: str, action: str = "access") -> bool:
        """Validate if user status allows the action"""
        if status == UserStatus.APPROVED:
            return True
        elif status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đang chờ duyệt từ admin"
            )
        elif status == UserStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị từ chối"
            )
        elif status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị tạm ngưng"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản không hoạt động"
            )
    
    @staticmethod
    def check_permission(user_role: str, required_roles: list[str]) -> bool:
        """Check if user role has permission"""
        role_hierarchy = {
            UserRole.SUPER_ADMIN: 5,
            UserRole.ADMIN: 4,
            UserRole.MANAGER: 3,
            UserRole.ANALYST: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = min([role_hierarchy.get(role, 0) for role in required_roles])
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện hành động này"
            )
        
        return True


# Singleton instance
auth_service = AuthService()
