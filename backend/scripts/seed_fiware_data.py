#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Seed Demo Data - FiWARE Smart Data Models
Tạo dữ liệu mở demo theo chuẩn NGSI-LD từ nguồn thực tế Việt Nam
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from random import uniform, randint, choice
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.services.ngsi_ld_service import NGSILDEntityService
from app.schemas.fiware.civic_issue import CivicIssueTrackingCreate, IssueStatus, IssuePriority
from app.schemas.fiware.parking import ParkingSpotCreate


# Hanoi districts and their coordinates
HANOI_LOCATIONS = [
    {"name": "Ba Đình", "lat": 21.0355, "lon": 105.8198},
    {"name": "Hoàn Kiếm", "lat": 21.0285, "lon": 105.8542},
    {"name": "Hai Bà Trưng", "lat": 21.0069, "lon": 105.8523},
    {"name": "Đống Đa", "lat": 21.0169, "lon": 105.8341},
    {"name": "Thanh Xuân", "lat": 20.9947, "lon": 105.8045},
    {"name": "Cầu Giấy", "lat": 21.0333, "lon": 105.7944},
    {"name": "Tây Hồ", "lat": 21.0658, "lon": 105.8194},
    {"name": "Hoàng Mai", "lat": 20.9745, "lon": 105.8516},
    {"name": "Long Biên", "lat": 21.0505, "lon": 105.8970},
    {"name": "Hà Đông", "lat": 20.9719, "lon": 105.7795},
]

# Civic issue categories from Vietnam
CIVIC_ISSUES_DATA = [
    {
        "category": "streetLighting",
        "subCategory": "brokenLight",
        "title": "Đèn đường hỏng trên đường {street}",
        "description": "Đèn đường tại vị trí này đã hỏng trong vài ngày qua, gây nguy hiểm cho người đi đường vào ban đêm. Cần sửa chữa khẩn cấp."
    },
    {
        "category": "roadDamage",
        "subCategory": "pothole",
        "title": "Ổ gà lớn trên đường {street}",
        "description": "Có ổ gà sâu khoảng 20cm, nguy hiểm cho xe máy. Nhiều người đã bị ngã tại vị trí này."
    },
    {
        "category": "roadDamage",
        "subCategory": "floodedRoad",
        "title": "Đường ngập nước sau mưa tại {street}",
        "description": "Mỗi khi mưa, khu vực này bị ngập sâu 30-40cm do hệ thống thoát nước kém. Gây khó khăn cho việc di chuyển."
    },
    {
        "category": "waste",
        "subCategory": "overflowingBin",
        "title": "Thùng rác tràn lan tại {street}",
        "description": "Thùng rác công cộng đã đầy nhưng không được thu gom kịp thời, rác tràn ra đường gây ô nhiễm và mùi hôi."
    },
    {
        "category": "drainage",
        "subCategory": "blockedDrain",
        "title": "Cống thoát nước bị tắc nghẽn tại {street}",
        "description": "Cống thoát nước bị rác và bùn đất làm tắc nghẽn, nước không thoát được khi mưa."
    },
    {
        "category": "sidewalk",
        "subCategory": "brokenPavement",
        "title": "Vỉa hè hư hỏng tại {street}",
        "description": "Gạch vỉa hè bị vỡ, lún, nguy hiểm cho người đi bộ đặc biệt là người già và trẻ em."
    },
    {
        "category": "publicSpace",
        "subCategory": "illegalParking",
        "title": "Xe lấn chiếm lòng đường tại {street}",
        "description": "Nhiều xe ô tô, xe máy đỗ trên vỉa hè và lòng đường, gây cản trở giao thông."
    },
    {
        "category": "environment",
        "subCategory": "airPollution",
        "title": "Ô nhiễm không khí nghiêm trọng gần {street}",
        "description": "Khói bụi từ công trường xây dựng gây ô nhiễm không khí nghiêm trọng, ảnh hưởng đến sức khỏe người dân."
    },
    {
        "category": "publicFacility",
        "subCategory": "damagedBench",
        "title": "Ghế công viên hư hỏng tại {street}",
        "description": "Ghế ngồi trong công viên bị gãy, cần sửa chữa hoặc thay thế."
    },
    {
        "category": "vegetation",
        "subCategory": "overgrown",
        "title": "Cây cối mọc quá tầm che mất tầm nhìn tại {street}",
        "description": "Cây xanh mọc quá tầm, che khuất biển báo và tầm nhìn người điều khiển phương tiện."
    }
]

# Vietnamese street names
STREET_NAMES = [
    "Giải Phóng", "Láng Hạ", "Nguyễn Trãi", "Xã Đàn", 
    "Kim Mã", "Phạm Ngọc Thạch", "Tôn Đức Thắng", "Trần Hưng Đạo",
    "Lý Thường Kiệt", "Bà Triệu", "Điện Biên Phủ", "Nguyễn Chí Thanh",
    "Hoàng Quốc Việt", "Cầu Giấy", "Xuân Thủy", "Trần Duy Hưng"
]

# Reporter names (Vietnamese)
REPORTER_NAMES = [
    "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung",
    "Hoàng Văn Em", "Vũ Thị Hoa", "Đặng Văn Khánh", "Bùi Thị Lan",
    "Ngô Văn Minh", "Phan Thị Nga"
]


async def seed_civic_issues(service: NGSILDEntityService, count: int = 50):
    """Seed civic issue tracking entities"""
    print(f"\n🏙️  Seeding {count} civic issues...")
    
    for i in range(count):
        # Random location in Hanoi
        loc = choice(HANOI_LOCATIONS)
        lat = loc["lat"] + uniform(-0.01, 0.01)
        lon = loc["lon"] + uniform(-0.01, 0.01)
        
        # Random issue template
        issue_template = choice(CIVIC_ISSUES_DATA)
        street = choice(STREET_NAMES)
        
        # Random dates
        days_ago = randint(1, 30)
        created = datetime.utcnow() - timedelta(days=days_ago)
        
        # Random status
        statuses = [IssueStatus.OPEN, IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED, IssueStatus.CLOSED]
        status = choice(statuses)
        
        # Create entity
        issue = CivicIssueTrackingCreate(
            location={"type": "Point", "coordinates": [lon, lat]},
            address={
                "streetAddress": street,
                "addressLocality": loc["name"],
                "addressRegion": "Hanoi",
                "addressCountry": "VN"
            },
            title=issue_template["title"].format(street=street),
            description=issue_template["description"],
            category=issue_template["category"],
            subCategory=issue_template["subCategory"],
            status=status,
            priority=choice([IssuePriority.LOW, IssuePriority.MEDIUM, IssuePriority.HIGH]),
            reportedBy=choice(REPORTER_NAMES),
            reporterEmail=f"reporter{i}@example.com",
            upvotes=randint(0, 50),
            downvotes=randint(0, 10),
            comments=randint(0, 20),
            dateCreated=created,
            dateModified=created + timedelta(days=randint(0, days_ago)) if status != IssueStatus.OPEN else None,
            dateResolved=created + timedelta(days=randint(days_ago, days_ago+5)) if status == IssueStatus.RESOLVED else None
        )
        
        # Convert to NGSI-LD and store
        from app.schemas.fiware.civic_issue import to_ngsi_ld_entity
        entity_id = f"urn:ngsi-ld:CivicIssueTracking:Hanoi:{created.strftime('%Y%m%d')}-{i:03d}"
        entity = to_ngsi_ld_entity(issue, entity_id)
        
        await service.store_entity(entity)
        
        if (i + 1) % 10 == 0:
            print(f"  ✓ Created {i + 1}/{count} civic issues")
    
    print(f"Successfully seeded {count} civic issues")


async def seed_parking_spots(service: NGSILDEntityService, count: int = 100):
    """Seed parking spot entities"""
    print(f"\n🅿Seeding {count} parking spots...")
    
    parking_sites = [
        "Times City", "Royal City", "Vincom Center", "Lotte Center",
        "Big C", "Aeon Mall", "Parkson", "Landmark 72"
    ]
    
    for i in range(count):
        # Random location in Hanoi
        loc = choice(HANOI_LOCATIONS)
        lat = loc["lat"] + uniform(-0.005, 0.005)
        lon = loc["lon"] + uniform(-0.005, 0.005)
        
        site = choice(parking_sites)
        floor = choice(["B1", "B2", "B3", "G", "1", "2"])
        
        parking = ParkingSpotCreate(
            location={"type": "Point", "coordinates": [lon, lat]},
            address={
                "addressLocality": loc["name"],
                "addressRegion": "Hanoi",
                "addressCountry": "VN"
            },
            name=f"Spot {floor}-{i:03d}",
            category="offStreet",
            status=choice(["free", "occupied", "free", "free"]),  # 75% free
            allowedVehicleType=choice(["car", "motorcycle"]),
            refParkingSite=f"urn:ngsi-ld:ParkingSite:Hanoi:{site.replace(' ', '')}",
            dateModified=datetime.utcnow()
        )
        
        # Convert to NGSI-LD and store
        from app.schemas.fiware.parking import to_ngsi_ld_entity
        entity_id = f"urn:ngsi-ld:ParkingSpot:Hanoi:{site.replace(' ', '')}-{floor}-{i:03d}"
        entity = to_ngsi_ld_entity(parking, entity_id)
        
        await service.store_entity(entity)
        
        if (i + 1) % 20 == 0:
            print(f"  ✓ Created {i + 1}/{count} parking spots")
    
    print(f"Successfully seeded {count} parking spots")


async def seed_realtime_data(service: NGSILDEntityService):
    """Seed current real-time weather and air quality data"""
    print("\nFetching and storing real-time data...")
    
    try:
        # Sync weather data for Hanoi
        print("Fetching weather data...")
        await service.sync_weather_data(21.028511, 105.804817, "Hanoi")
        print("  ✓ Weather data stored")
        
        # Sync air quality data
        print("Fetching air quality data...")
        await service.sync_air_quality_data("hanoi")
        print("  ✓ Air quality data stored")
        
        print("Real-time data synchronized")
    except Exception as e:
        print(f"Warning: Could not sync real-time data: {e}")


async def main():
    """Main seeding function"""
    print("=" * 60)
    print("  CityLens - FiWARE Smart Data Models Demo Seeder")
    print("  Dữ liệu mở theo chuẩn NGSI-LD từ thực tế Việt Nam")
    print("=" * 60)
    
    # Create async engine
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        service = NGSILDEntityService(session)
        
        # Seed civic issues (Báo cáo từ người dân)
        await seed_civic_issues(service, count=50)
        
        # Seed parking spots
        await seed_parking_spots(service, count=100)
        
        # Sync real-time data
        await seed_realtime_data(service)
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("Demo data seeding completed!")
    print("Access NGSI-LD API: http://localhost:8000/api/v1/ngsi-ld/v1/entities")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
