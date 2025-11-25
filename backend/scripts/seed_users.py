#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Seed sample users và test reports
Chạy: python scripts/seed_users.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.postgres import SessionLocal, engine
from app.models.user import User, UserRole, Base
from app.models.report import Report, ReportStatus, ReportPriority
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

Base.metadata.create_all(bind=engine)


def seed_users():
    """Seed sample users"""
    db: Session = SessionLocal()
    
    users_data = [
        {
            "email": "admin@citylens.io",
            "username": "admin",
            "full_name": "Admin CityLens",
            "role": UserRole.ADMIN,
            "password": "Admin@123"
        },
        {
            "email": "moderator@citylens.io",
            "username": "moderator",
            "full_name": "Moderator CityLens",
            "role": UserRole.MODERATOR,
            "password": "Mod@123"
        },
        {
            "email": "nguyen.van.a@gmail.com",
            "username": "nguyenvana",
            "full_name": "Nguyễn Văn A",
            "phone": "0901234567",
            "role": UserRole.CITIZEN,
            "password": "User@123"
        },
        {
            "email": "tran.thi.b@gmail.com",
            "username": "tranthib",
            "full_name": "Trần Thị B",
            "phone": "0912345678",
            "role": UserRole.CITIZEN,
            "password": "User@123"
        },
        {
            "email": "le.van.c@gmail.com",
            "username": "levanc",
            "full_name": "Lê Văn C",
            "phone": "0923456789",
            "role": UserRole.CITIZEN,
            "password": "User@123"
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing:
            print(f"- User already exists: {user_data['email']}")
            created_users.append(existing)
            continue
        
        password = user_data.pop("password")
        user = User(
            **user_data,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_verified=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        print(f"✓ Created user: {user.email} (role: {user.role.value})")
    
    print(f"\n✅ Created {len([u for u in users_data if not db.query(User).filter(User.email == u['email']).first()])} users")
    db.close()
    
    return created_users


def seed_sample_reports():
    """Seed sample reports"""
    db: Session = SessionLocal()
    
    # Get users
    users = db.query(User).filter(User.role == UserRole.CITIZEN).all()
    if not users:
        print("❌ No users found. Run seed_users() first!")
        return
    
    # Sample locations in Ho Chi Minh City
    sample_locations = [
        {"lat": 10.762622, "lon": 106.660172, "address": "Đường Lê Lợi, Quận 1", "district_id": 1},
        {"lat": 10.776889, "lon": 106.695801, "address": "Đường Lê Văn Việt, Quận 9", "district_id": 9},
        {"lat": 10.771420, "lon": 106.697800, "address": "Đường Phạm Văn Đồng, Thủ Đức", "district_id": 2},
        {"lat": 10.729360, "lon": 106.691654, "address": "Đường Nguyễn Văn Linh, Quận 7", "district_id": 7},
        {"lat": 10.801953, "lon": 106.663841, "address": "Đường Hồng Bàng, Quận 11", "district_id": 11},
    ]
    
    sample_reports = [
        {
            "category": "giao_thong",
            "subcategory": "duong_hong",
            "title": "Đường Lê Lợi có ổ gà lớn",
            "description": "Ổ gà sâu khoảng 20cm, rộng 50cm, gây nguy hiểm cho phương tiện. Cần sửa chữa gấp!",
            "priority": ReportPriority.HIGH
        },
        {
            "category": "moi_truong",
            "subcategory": "rac_thai",
            "title": "Rác thải tràn ra đường",
            "description": "Thùng rác công cộng đầy tràn, rác bị tràn ra đường, gây mất vệ sinh.",
            "priority": ReportPriority.NORMAL
        },
        {
            "category": "ha_tang",
            "subcategory": "via_he",
            "title": "Vỉa hè bị hư hỏng",
            "description": "Vỉa hè nhiều chỗ bị lún, gạch vỡ, khó đi lại.",
            "priority": ReportPriority.NORMAL
        },
        {
            "category": "giao_thong",
            "subcategory": "den_tin_hieu",
            "title": "Đèn giao thông không hoạt động",
            "description": "Đèn tín hiệu tại ngã tư không hoạt động từ sáng nay, gây ùn tắc.",
            "priority": ReportPriority.URGENT
        },
        {
            "category": "moi_truong",
            "subcategory": "cay_xanh",
            "title": "Cây đổ chắn đường",
            "description": "Cây to đổ sau mưa bão, chắn ngang đường.",
            "priority": ReportPriority.URGENT
        },
    ]
    
    statuses = [ReportStatus.PENDING, ReportStatus.VERIFIED, ReportStatus.IN_PROGRESS]
    
    created_count = 0
    for i, report_data in enumerate(sample_reports):
        location = sample_locations[i % len(sample_locations)]
        user = random.choice(users)
        
        report = Report(
            user_id=user.id,
            category=report_data["category"],
            subcategory=report_data.get("subcategory"),
            title=report_data["title"],
            description=report_data["description"],
            location=f'SRID=4326;POINT({location["lon"]} {location["lat"]})',
            address=location["address"],
            district_id=location["district_id"],
            status=random.choice(statuses),
            priority=report_data.get("priority", ReportPriority.NORMAL),
            upvotes=random.randint(5, 50),
            downvotes=random.randint(0, 5),
            views=random.randint(50, 500),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        
        db.add(report)
        created_count += 1
    
    db.commit()
    print(f"✅ Created {created_count} sample reports")
    db.close()


if __name__ == "__main__":
    print("🌱 Seeding users...")
    users = seed_users()
    
    print("\n🌱 Seeding sample reports...")
    seed_sample_reports()
    
    print("\n✅ All seed data completed!")
    print("\nTest accounts:")
    print("  Admin: admin@citylens.io / Admin@123")
    print("  Mod: moderator@citylens.io / Mod@123")
    print("  User: nguyen.van.a@gmail.com / User@123")
