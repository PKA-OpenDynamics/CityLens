#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Seed report categories vào database
Chạy: python scripts/seed_categories.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.db.postgres import engine, SessionLocal
from app.models.report import ReportCategory, Base

# Tạo tables nếu chưa có
Base.metadata.create_all(bind=engine)


def seed_categories():
    """Seed report categories"""
    db: Session = SessionLocal()
    
    categories = [
        # Main categories
        {
            "code": "giao_thong",
            "name_vi": "Giao thông",
            "name_en": "Transportation",
            "description": "Các vấn đề về giao thông, đường bộ",
            "icon": "traffic",
            "color": "#FF5722",
            "display_order": 1
        },
        {
            "code": "moi_truong",
            "name_vi": "Môi trường",
            "name_en": "Environment",
            "description": "Ô nhiễm, rác thải, vệ sinh môi trường",
            "icon": "eco",
            "color": "#4CAF50",
            "display_order": 2
        },
        {
            "code": "ha_tang",
            "name_vi": "Hạ tầng",
            "name_en": "Infrastructure",
            "description": "Cơ sở hạ tầng, công trình công cộng",
            "icon": "construction",
            "color": "#2196F3",
            "display_order": 3
        },
        {
            "code": "an_ninh",
            "name_vi": "An ninh trật tự",
            "name_en": "Public Safety",
            "description": "An ninh, trật tự công cộng",
            "icon": "security",
            "color": "#F44336",
            "display_order": 4
        },
        {
            "code": "dich_vu",
            "name_vi": "Dịch vụ công",
            "name_en": "Public Services",
            "description": "Dịch vụ công, tiện ích",
            "icon": "room_service",
            "color": "#9C27B0",
            "display_order": 5
        },
        {
            "code": "khac",
            "name_vi": "Khác",
            "name_en": "Others",
            "description": "Các vấn đề khác",
            "icon": "more_horiz",
            "color": "#607D8B",
            "display_order": 6
        }
    ]
    
    # Insert main categories
    main_cats = {}
    for cat_data in categories:
        existing = db.query(ReportCategory).filter(
            ReportCategory.code == cat_data["code"]
        ).first()
        
        if not existing:
            cat = ReportCategory(**cat_data)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            main_cats[cat_data["code"]] = cat.id
            print(f"✓ Created category: {cat_data['name_vi']}")
        else:
            main_cats[cat_data["code"]] = existing.id
            print(f"- Category already exists: {cat_data['name_vi']}")
    
    # Subcategories
    subcategories = [
        # Giao thông
        {"code": "duong_hong", "name_vi": "Đường hư hỏng", "name_en": "Road damage", "parent": "giao_thong"},
        {"code": "tai_nan", "name_vi": "Tai nạn giao thông", "name_en": "Traffic accident", "parent": "giao_thong"},
        {"code": "un_tac", "name_vi": "Ùn tắc giao thông", "name_en": "Traffic jam", "parent": "giao_thong"},
        {"code": "bien_bao", "name_vi": "Biển báo hư", "name_en": "Damaged sign", "parent": "giao_thong"},
        {"code": "den_tin_hieu", "name_vi": "Đèn tín hiệu hỏng", "name_en": "Traffic light broken", "parent": "giao_thong"},
        
        # Môi trường
        {"code": "rac_thai", "name_vi": "Rác thải bừa bãi", "name_en": "Littering", "parent": "moi_truong"},
        {"code": "o_nhiem_kk", "name_vi": "Ô nhiễm không khí", "name_en": "Air pollution", "parent": "moi_truong"},
        {"code": "o_nhiem_nuoc", "name_vi": "Ô nhiễm nước", "name_en": "Water pollution", "parent": "moi_truong"},
        {"code": "cay_xanh", "name_vi": "Cây xanh đổ, cần chăm sóc", "name_en": "Tree fallen/maintenance", "parent": "moi_truong"},
        {"code": "tieng_on", "name_vi": "Tiếng ồn", "name_en": "Noise pollution", "parent": "moi_truong"},
        
        # Hạ tầng
        {"code": "cong_trinh", "name_vi": "Công trình hư hỏng", "name_en": "Infrastructure damage", "parent": "ha_tang"},
        {"code": "duong_ong", "name_vi": "Đường ống nước vỡ", "name_en": "Water pipe burst", "parent": "ha_tang"},
        {"code": "dien_luc", "name_vi": "Sự cố điện", "name_en": "Power outage", "parent": "ha_tang"},
        {"code": "cong_cong", "name_vi": "Cống thoát nước", "name_en": "Drainage", "parent": "ha_tang"},
        {"code": "via_he", "name_vi": "Vỉa hè hư", "name_en": "Sidewalk damage", "parent": "ha_tang"},
        
        # An ninh
        {"code": "trom_cap", "name_vi": "Trộm cắp", "name_en": "Theft", "parent": "an_ninh"},
        {"code": "dam_nhau", "name_vi": "Đánh nhau", "name_en": "Fighting", "parent": "an_ninh"},
        {"code": "nguoi_say", "name_vi": "Người say gây rối", "name_en": "Drunk disturbance", "parent": "an_ninh"},
        {"code": "lua_dao", "name_vi": "Lừa đảo", "name_en": "Fraud", "parent": "an_ninh"},
        
        # Dịch vụ công
        {"code": "y_te", "name_vi": "Vấn đề y tế", "name_en": "Healthcare issue", "parent": "dich_vu"},
        {"code": "giao_duc", "name_vi": "Giáo dục", "name_en": "Education", "parent": "dich_vu"},
        {"code": "hanh_chinh", "name_vi": "Thủ tục hành chính", "name_en": "Administrative procedure", "parent": "dich_vu"},
    ]
    
    for sub_data in subcategories:
        existing = db.query(ReportCategory).filter(
            ReportCategory.code == sub_data["code"]
        ).first()
        
        if not existing:
            parent_code = sub_data.pop("parent")
            sub_data["parent_id"] = main_cats.get(parent_code)
            sub = ReportCategory(**sub_data)
            db.add(sub)
            db.commit()
            print(f"  ✓ Created subcategory: {sub_data['name_vi']}")
    
    print(f"\n✅ Seed categories completed!")
    db.close()


if __name__ == "__main__":
    print("🌱 Seeding report categories...")
    seed_categories()
