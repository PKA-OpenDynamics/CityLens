#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Seed Super Admin User for CityLens Dashboard
Creates the first super admin account to manage the system
"""

import sys
import os
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.auth_service import auth_service
from app.schemas.user import UserRole, UserStatus


async def seed_super_admin():
    """Create super admin user"""
    
    print("🔐 CityLens Super Admin Seeder")
    print("=" * 60)
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    users_collection = db.users
    
    print(f"✅ Connected to MongoDB: {settings.MONGODB_URL}")
    print(f"📦 Database: {settings.MONGODB_DB}")
    
    # Super Admin credentials
    super_admin = {
        "email": "admin@citylens.com",
        "password": "Admin@2025",  # Should be changed on first login
        "full_name": "Super Administrator",
        "phone": "+84 24 3825 9001",
        "department": "Sở Thông tin và Truyền thông Hà Nội",
        "position": "Quản trị viên hệ thống",
        "reason": "Tài khoản quản trị viên chính của hệ thống CityLens"
    }
    
    # Check if super admin already exists
    existing_admin = await users_collection.find_one({"email": super_admin["email"]})
    
    if existing_admin:
        print(f"\n⚠️  Super admin đã tồn tại: {super_admin['email']}")
        print(f"📧 Email: {existing_admin['email']}")
        print(f"👤 Tên: {existing_admin['full_name']}")
        print(f"🔑 Vai trò: {existing_admin['role']}")
        print(f"📅 Tạo lúc: {existing_admin['created_at']}")
        client.close()
        return
    
    # Hash password
    hashed_password = auth_service.get_password_hash(super_admin["password"])
    
    # Create super admin document
    admin_doc = {
        "email": super_admin["email"],
        "hashed_password": hashed_password,
        "full_name": super_admin["full_name"],
        "phone": super_admin["phone"],
        "department": super_admin["department"],
        "position": super_admin["position"],
        "reason": super_admin["reason"],
        "role": UserRole.SUPER_ADMIN,
        "status": UserStatus.APPROVED,  # Auto-approved
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "approved_by": "system",
        "approved_at": datetime.utcnow(),
        "rejection_reason": None,
        "avatar_url": None
    }
    
    # Insert super admin
    result = await users_collection.insert_one(admin_doc)
    
    print(f"\n✅ Đã tạo Super Admin thành công!")
    print(f"📧 Email: {super_admin['email']}")
    print(f"🔑 Password: {super_admin['password']} (⚠️  PHẢI ĐỔI MẬT KHẨU SAU KHI ĐĂNG NHẬP LẦN ĐẦU)")
    print(f"👤 Tên: {super_admin['full_name']}")
    print(f"🏢 Phòng ban: {super_admin['department']}")
    print(f"💼 Chức vụ: {super_admin['position']}")
    print(f"🆔 ID: {result.inserted_id}")
    
    # Create indexes
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("status")
    await users_collection.create_index("role")
    await users_collection.create_index("created_at")
    
    print(f"\n📊 Đã tạo indexes cho users collection")
    
    # Also create a few test users for demo
    print(f"\n👥 Tạo các user demo...")
    
    demo_users = [
        {
            "email": "manager.gtvt@citylens.com",
            "password": "Manager@2025",
            "full_name": "Nguyễn Văn An",
            "phone": "+84 98 765 4321",
            "department": "Sở Giao thông Vận tải",
            "position": "Phó giám đốc",
            "reason": "Quản lý hệ thống giao thông và đỗ xe",
            "role": UserRole.MANAGER,
            "status": UserStatus.APPROVED
        },
        {
            "email": "analyst.moitruong@citylens.com",
            "password": "Analyst@2025",
            "full_name": "Trần Thị Bình",
            "phone": "+84 97 654 3210",
            "department": "Sở Tài nguyên và Môi trường",
            "position": "Chuyên viên phân tích",
            "reason": "Theo dõi chất lượng không khí và môi trường",
            "role": UserRole.ANALYST,
            "status": UserStatus.APPROVED
        },
        {
            "email": "pending.user@citylens.com",
            "password": "User@2025",
            "full_name": "Phạm Văn Cường",
            "phone": "+84 96 543 2109",
            "department": "Sở Xây dựng",
            "position": "Chuyên viên",
            "reason": "Xin quyền truy cập để theo dõi báo cáo sự cố",
            "role": UserRole.VIEWER,
            "status": UserStatus.PENDING  # Chờ duyệt
        }
    ]
    
    for user_data in demo_users:
        existing = await users_collection.find_one({"email": user_data["email"]})
        if not existing:
            hashed_pw = auth_service.get_password_hash(user_data.pop("password"))
            
            user_doc = {
                **user_data,
                "hashed_password": hashed_pw,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None,
                "approved_by": "system" if user_data["status"] == UserStatus.APPROVED else None,
                "approved_at": datetime.utcnow() if user_data["status"] == UserStatus.APPROVED else None,
                "rejection_reason": None,
                "avatar_url": None
            }
            
            await users_collection.insert_one(user_doc)
            print(f"   ✅ {user_data['email']} - {user_data['role']} - {user_data['status']}")
    
    # Count users
    total_users = await users_collection.count_documents({})
    pending_users = await users_collection.count_documents({"status": UserStatus.PENDING})
    approved_users = await users_collection.count_documents({"status": UserStatus.APPROVED})
    
    print(f"\n📊 Thống kê users:")
    print(f"   Tổng số: {total_users}")
    print(f"   Đã duyệt: {approved_users}")
    print(f"   Chờ duyệt: {pending_users}")
    
    print(f"\n🎉 Hoàn thành! Bây giờ bạn có thể đăng nhập vào dashboard.")
    print(f"📱 API Docs: http://localhost:8000/docs")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_super_admin())
