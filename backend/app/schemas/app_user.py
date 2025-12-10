# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App User Schema
Compatible with web-app/server UserProfile model
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class AppUserRegister(BaseModel):
    """Mobile app user registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1)
    phone: Optional[str] = None


class AppUserLogin(BaseModel):
    """Mobile app user login request"""
    username: str
    password: str


class AppUserProfile(BaseModel):
    """Mobile app user profile (matches web-app/server model)"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str
    email: str
    full_name: str
    phone: Optional[str] = ""
    is_active: bool = True
    role: str = "user"
    level: int = 1
    points: int = 0
    reputation_score: int = 0
    is_verified: bool = False
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AppUserInDB(AppUserProfile):
    """User with hashed password (not exposed to API)"""
    password: str


class AppTokenResponse(BaseModel):
    """Mobile app token response"""
    success: bool = True
    data: dict  # Contains: user, access_token, token_type


class AppUserUpdate(BaseModel):
    """Mobile app user profile update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
