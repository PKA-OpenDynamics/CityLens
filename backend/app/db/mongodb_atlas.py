# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
MongoDB Atlas Connection for Mobile App
Handles connection to cloud MongoDB for mobile app authentication and reports
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings

class MongoDBAtlas:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        if not settings.MONGODB_ATLAS_URI:
            raise ValueError("MONGODB_ATLAS_URI is not configured")
        
        self.client = AsyncIOMotorClient(settings.MONGODB_ATLAS_URI)
        self.db = self.client[settings.MONGODB_ATLAS_DB]
        
        # Test connection
        await self.client.admin.command('ping')
        print(f"✅ Connected to MongoDB Atlas: {settings.MONGODB_ATLAS_DB}")
    
    async def close(self):
        """Close MongoDB Atlas connection"""
        if self.client:
            self.client.close()
            print("✅ Closed MongoDB Atlas connection")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if self.db is None:
            raise RuntimeError("MongoDB Atlas not connected")
        return self.db


# Singleton instance
mongodb_atlas = MongoDBAtlas()


async def get_mongodb_atlas() -> AsyncIOMotorDatabase:
    """Dependency to get MongoDB Atlas database"""
    return mongodb_atlas.get_database()
