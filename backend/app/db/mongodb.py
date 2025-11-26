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
