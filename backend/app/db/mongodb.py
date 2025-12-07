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
    - Raw: 24 hours (realtime data, ~17,280 docs/day will auto-delete)
    - Hourly: 7 days
    - Daily: 90 days (to keep historical data for analysis)
    - Monthly: permanent (no TTL)
    """
    async def create_index_safe(collection, index_spec, **options):
        """Safely create index, handling conflicts"""
        try:
            await collection.create_index(index_spec, **options)
        except Exception as e:
            # If index already exists with different name, drop old and create new
            if "already exists with a different name" in str(e) or "IndexOptionsConflict" in str(e):
                # Find and drop existing index with same keys
                existing_indexes = await collection.list_indexes().to_list(length=100)
                # Convert index_spec to dict format for comparison
                if isinstance(index_spec, list):
                    index_dict = dict(index_spec)
                elif isinstance(index_spec, str):
                    index_dict = {index_spec: 1}
                else:
                    index_dict = dict(index_spec)
                
                for idx in existing_indexes:
                    if idx.get("key") == index_dict:
                        await collection.drop_index(idx["name"])
                        # Retry creating with new name
                        await collection.create_index(index_spec, **options)
                        break
            elif "already exists" in str(e).lower():
                # Index already exists with same name, skip
                pass
            else:
                # For other errors, just log and continue
                print(f"  ⚠️  Index creation warning: {e}")
    
    # Raw collection - 24h TTL
    # Note: For realtime data (1 min interval with 12 locations):
    # - Documents per day: 12 × 60 × 24 = 17,280 docs/day
    # - With TTL 24h: ~17,280 docs will be deleted each day (1 day's worth of data)
    raw_col = database["weather_raw"]
    await create_index_safe(raw_col, "location_id")
    await create_index_safe(raw_col, "timestamp")
    await create_index_safe(raw_col, [("location_id", 1), ("timestamp", -1)])
    await create_index_safe(raw_col, [("coordinates", "2dsphere")])
    await create_index_safe(
        raw_col,
        [("created_at", 1)],
        expireAfterSeconds=86400,  # 24 hours
        name="ttl_24h"
    )
    
    # Hourly collection - 7 days TTL
    hourly_col = database["weather_hourly"]
    await create_index_safe(hourly_col, "location_id")
    await create_index_safe(hourly_col, "hour")
    await create_index_safe(hourly_col, [("location_id", 1), ("hour", -1)])
    await create_index_safe(
        hourly_col,
        [("created_at", 1)],
        expireAfterSeconds=604800,  # 7 days
        name="ttl_7d"
    )
    
    # Daily collection - 90 days TTL
    daily_col = database["weather_daily"]
    await create_index_safe(daily_col, "location_id")
    await create_index_safe(daily_col, "date")
    await create_index_safe(daily_col, [("location_id", 1), ("date", -1)])
    await create_index_safe(
        daily_col,
        [("created_at", 1)],
        expireAfterSeconds=7776000,  # 90 days (90 * 24 * 60 * 60)
        name="ttl_90d"
    )
    
    # Monthly collection - NO TTL (permanent for LOD)
    monthly_col = database["weather_monthly"]
    await create_index_safe(monthly_col, "location_id")
    await create_index_safe(monthly_col, [("year", 1), ("month", 1)])
    await create_index_safe(monthly_col, [("location_id", 1), ("year", -1), ("month", -1)])
    
    # Locations collection
    locations_col = database["weather_locations"]
    await create_index_safe(locations_col, "location_id", unique=True)
    await create_index_safe(locations_col, [("coordinates", "2dsphere")])
    
    print("✅ MongoDB indexes created successfully")