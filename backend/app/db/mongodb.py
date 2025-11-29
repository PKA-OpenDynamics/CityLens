# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Kết nối MongoDB
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.MONGODB_DB]


async def get_mongodb():
    """Dependency để lấy MongoDB database"""
    return database


# Collections
def get_citizen_reports_collection():
    return database["citizen_reports"]


def get_realtime_events_collection():
    return database["realtime_events"]


def get_user_profiles_collection():
    return database["user_profiles"]


def get_notifications_collection():
    return database["notifications"]


def get_audit_logs_collection():
    return database["audit_logs"]


# Weather Collections
def get_weather_raw_collection():
    return database["weather_raw"]


def get_weather_hourly_collection():
    return database["weather_hourly"]


def get_weather_daily_collection():
    return database["weather_daily"]


def get_weather_weekly_collection():
    return database["weather_weekly"]


def get_weather_monthly_collection():
    return database["weather_monthly"]


def get_weather_locations_collection():
    return database["weather_locations"]


async def connect_db():
    """Connect to MongoDB (placeholder for app startup)"""
    pass


async def close_db():
    """Close MongoDB connection (placeholder for app shutdown)"""
    if client:
        client.close()


async def setup_indexes():
    """
    Create indexes including TTL for data retention
    
    TTL Strategy:
    - Raw: 24 hours
    - Hourly: 7 days
    - Daily: 30 days
    - Weekly: 180 days (6 months)
    - Monthly: permanent (no TTL)
    """
    # Raw collection - 24h TTL
    raw_col = database["weather_raw"]
    await raw_col.create_index("location_id")
    await raw_col.create_index("timestamp")
    await raw_col.create_index([("location_id", 1), ("timestamp", -1)])
    await raw_col.create_index([("coordinates", "2dsphere")])
    await raw_col.create_index(
        [("created_at", 1)],
        expireAfterSeconds=86400  # 24 hours
    )
    
    # Hourly collection - 7 days TTL
    hourly_col = database["weather_hourly"]
    await hourly_col.create_index("location_id")
    await hourly_col.create_index("hour")
    await hourly_col.create_index([("location_id", 1), ("hour", -1)])
    await hourly_col.create_index(
        [("created_at", 1)],
        expireAfterSeconds=604800  # 7 days
    )
    
    # Daily collection - 30 days TTL
    daily_col = database["weather_daily"]
    await daily_col.create_index("location_id")
    await daily_col.create_index("date")
    await daily_col.create_index([("location_id", 1), ("date", -1)])
    await daily_col.create_index(
        [("created_at", 1)],
        expireAfterSeconds=2592000  # 30 days
    )
    
    # Weekly collection - 180 days TTL (6 months)
    weekly_col = database["weather_weekly"]
    await weekly_col.create_index("location_id")
    await weekly_col.create_index([("year", 1), ("week", 1)])
    await weekly_col.create_index([("location_id", 1), ("year", -1), ("week", -1)])
    await weekly_col.create_index(
        [("created_at", 1)],
        expireAfterSeconds=15552000  # 180 days
    )
    
    # Monthly collection - NO TTL (permanent for LOD)
    monthly_col = database["weather_monthly"]
    await monthly_col.create_index("location_id")
    await monthly_col.create_index([("year", 1), ("month", 1)])
    await monthly_col.create_index([("location_id", 1), ("year", -1), ("month", -1)])
    
    # Locations collection
    locations_col = database["weather_locations"]
    await locations_col.create_index("location_id", unique=True)
    await locations_col.create_index([("coordinates", "2dsphere")])
    
    print("✅ MongoDB indexes created successfully")