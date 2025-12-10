# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
MongoDB Database Connection
Manages async connection pool for user authentication and realtime data
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings

class MongoDB:
    """MongoDB connection manager using Motor (async driver)"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_db(cls):
        """Initialize MongoDB connection pool"""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=10,
                minPoolSize=2,
                serverSelectionTimeoutMS=5000
            )
            cls.db = cls.client[settings.MONGODB_DB]
            
            # Create indexes for users collection
            await cls.db.users.create_index("email", unique=True)
            await cls.db.users.create_index("status")
            await cls.db.users.create_index("role")
            await cls.db.users.create_index("created_at")
            
            print(f"✅ Connected to MongoDB: {settings.MONGODB_URL}")
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection pool"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None
            print("🔌 Closed MongoDB connection")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance"""
        if cls.db is None:
            raise RuntimeError("MongoDB not connected. Call connect_db() first.")
        return cls.db

# Global instance
mongodb = MongoDB()

async def get_mongodb() -> AsyncIOMotorDatabase:
    """FastAPI dependency for MongoDB database"""
    return mongodb.get_db()
