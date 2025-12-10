#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Create MongoDB Indexes for Performance Optimization
This script creates indexes on the reports collection for faster queries
Run this once to optimize database performance
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI")
MONGODB_ATLAS_DB_NAME = os.getenv("MONGODB_ATLAS_DB", "citylens_app")


async def create_indexes():
    """Create all necessary indexes for optimal query performance"""
    
    print(f"🔗 Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGODB_ATLAS_URI)
    db = client[MONGODB_ATLAS_DB_NAME]
    reports_collection = db.reports
    
    print(f"📊 Creating indexes on '{MONGODB_ATLAS_DB_NAME}.reports' collection...")
    
    # Define indexes
    indexes = [
        # Single field indexes
        IndexModel([("status", ASCENDING)], name="idx_status"),
        IndexModel([("userId", ASCENDING)], name="idx_userId"),
        IndexModel([("ward", ASCENDING)], name="idx_ward"),
        IndexModel([("reportType", ASCENDING)], name="idx_reportType"),
        IndexModel([("createdAt", DESCENDING)], name="idx_createdAt_desc"),
        
        # Compound indexes for common queries
        IndexModel(
            [("status", ASCENDING), ("createdAt", DESCENDING)],
            name="idx_status_createdAt"
        ),
        IndexModel(
            [("userId", ASCENDING), ("createdAt", DESCENDING)],
            name="idx_userId_createdAt"
        ),
        IndexModel(
            [("ward", ASCENDING), ("createdAt", DESCENDING)],
            name="idx_ward_createdAt"
        ),
        IndexModel(
            [("reportType", ASCENDING), ("createdAt", DESCENDING)],
            name="idx_reportType_createdAt"
        ),
        IndexModel(
            [("status", ASCENDING), ("userId", ASCENDING), ("createdAt", DESCENDING)],
            name="idx_status_userId_createdAt"
        ),
        
        # Geospatial index for location-based queries
        IndexModel([("location", "2dsphere")], name="idx_location_2dsphere"),
    ]
    
    try:
        # Create indexes
        result = await reports_collection.create_indexes(indexes)
        print(f"✅ Successfully created {len(result)} indexes:")
        for idx_name in result:
            print(f"   - {idx_name}")
        
        # List all indexes
        print(f"\n📋 Current indexes on reports collection:")
        indexes_info = await reports_collection.index_information()
        for idx_name, idx_info in indexes_info.items():
            keys = idx_info.get('key', [])
            print(f"   - {idx_name}: {keys}")
        
        # Get collection stats
        stats = await db.command("collStats", "reports")
        print(f"\n📈 Collection statistics:")
        print(f"   - Documents: {stats.get('count', 0):,}")
        print(f"   - Size: {stats.get('size', 0) / (1024*1024):.2f} MB")
        print(f"   - Storage Size: {stats.get('storageSize', 0) / (1024*1024):.2f} MB")
        print(f"   - Indexes: {stats.get('nindexes', 0)}")
        print(f"   - Total Index Size: {stats.get('totalIndexSize', 0) / 1024:.2f} KB")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        raise
    finally:
        client.close()
        print(f"\n✅ Done! Database indexes have been optimized.")


async def create_alerts_indexes():
    """Create indexes for alerts collection"""
    
    print(f"\n🔗 Creating indexes for alerts collection...")
    client = AsyncIOMotorClient(MONGODB_ATLAS_URI)
    db = client[MONGODB_ATLAS_DB_NAME]
    alerts_collection = db.mobile_alerts
    
    indexes = [
        IndexModel([("isActive", ASCENDING), ("createdAt", DESCENDING)], name="idx_isActive_createdAt"),
        IndexModel([("ward", ASCENDING), ("isActive", ASCENDING)], name="idx_ward_isActive"),
        IndexModel([("severity", ASCENDING), ("isActive", ASCENDING)], name="idx_severity_isActive"),
        IndexModel([("type", ASCENDING), ("createdAt", DESCENDING)], name="idx_type_createdAt"),
    ]
    
    try:
        result = await alerts_collection.create_indexes(indexes)
        print(f"✅ Created {len(result)} indexes for alerts collection")
    except Exception as e:
        print(f"❌ Error creating alerts indexes: {e}")
    finally:
        client.close()


async def main():
    """Main function"""
    print("=" * 60)
    print("🚀 MongoDB Performance Optimization")
    print("=" * 60)
    
    if not MONGODB_ATLAS_URI:
        print("❌ Error: MONGODB_ATLAS_URI environment variable not set")
        print("Please set it in your .env file")
        return
    
    await create_indexes()
    await create_alerts_indexes()
    
    print("\n" + "=" * 60)
    print("🎉 All indexes created successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
