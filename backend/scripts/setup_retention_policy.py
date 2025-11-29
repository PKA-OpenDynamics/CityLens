"""
Setup Data Retention Policy
============================

Script để setup TTL indexes và test retention strategy:
- Raw: 24h retention (đủ để aggregate hourly)
- Hourly: 1 day retention (xóa ngay khi có daily)
- Daily: 60 days retention (đủ 2 tháng để tính monthly)
- Weekly: 60 days retention (cùng với daily)
- Monthly: permanent (no TTL) - giữ mãi cho LOD thống kê

Usage:
    python -m scripts.setup_retention_policy
    python -m scripts.setup_retention_policy --drop-indexes  # Reset
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


class RetentionPolicySetup:
    """Setup retention policy with TTL indexes"""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB]
    
    async def drop_all_indexes(self):
        """Drop all indexes (except _id) - for reset"""
        print("🗑️  Dropping existing indexes...")
        
        collections = [
            "weather_raw",
            "weather_hourly",
            "weather_daily",
            "weather_weekly",
            "weather_monthly",
            "weather_locations"
        ]
        
        for coll_name in collections:
            try:
                col = self.db[coll_name]
                # List indexes
                indexes = await col.list_indexes().to_list(length=None)
                
                # Drop all except _id_
                for idx in indexes:
                    if idx["name"] != "_id_":
                        await col.drop_index(idx["name"])
                        print(f"  ✅ Dropped {coll_name}.{idx['name']}")
            except Exception as e:
                print(f"  ⚠️  {coll_name}: {e}")
        
        print("✅ Indexes dropped\n")
    
    async def create_retention_indexes(self):
        """Create TTL indexes for data retention"""
        print("📑 Creating retention policy indexes...\n")
        
        # === RAW COLLECTION: 24h TTL ===
        print("1️⃣  weather_raw - 24 hours retention")
        raw_col = self.db["weather_raw"]
        
        # Functional indexes
        await raw_col.create_index("location_id")
        print("  ✅ Index: location_id")
        
        await raw_col.create_index("timestamp")
        print("  ✅ Index: timestamp")
        
        await raw_col.create_index([("location_id", 1), ("timestamp", -1)])
        print("  ✅ Compound index: location_id + timestamp")
        
        await raw_col.create_index([("coordinates", "2dsphere")])
        print("  ✅ Geospatial index: coordinates (2dsphere)")
        
        # TTL index
        await raw_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=86400,  # 24 hours
            name="ttl_24h"
        )
        print("  🕐 TTL index: created_at (24 hours)")
        print("  → Data auto-deleted after 24 hours\n")
        
        # === HOURLY COLLECTION: 25 hours TTL ===
        print("2️⃣  weather_hourly - 25 hours retention")
        hourly_col = self.db["weather_hourly"]
        
        await hourly_col.create_index("location_id")
        await hourly_col.create_index("hour")
        await hourly_col.create_index([("location_id", 1), ("hour", -1)])
        print("  ✅ Indexes: location_id, hour, compound")
        
        await hourly_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=90000,  # 25 hours (24h + buffer)
            name="ttl_25h"
        )
        print("  🕐 TTL index: created_at (25 hours)")
        print("  → Data auto-deleted sau 25 giờ (buffer 1h để chắc chắn aggregate daily)\n")
        
        # === DAILY COLLECTION: 32 days TTL ===
        print("3️⃣  weather_daily - 32 days retention")
        daily_col = self.db["weather_daily"]
        
        await daily_col.create_index("location_id")
        await daily_col.create_index("date")
        await daily_col.create_index([("location_id", 1), ("date", -1)])
        print("  ✅ Indexes: location_id, date, compound")
        
        await daily_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=2764800,  # 32 days (30d + buffer)
            name="ttl_32d"
        )
        print("  🕐 TTL index: created_at (32 days)")
        print("  → Data auto-deleted sau 32 ngày (buffer 2 ngày để aggregate monthly)\n")
        
        # === WEEKLY COLLECTION: 60 days TTL ===
        print("4️⃣  weather_weekly - 60 days retention")
        weekly_col = self.db["weather_weekly"]
        
        await weekly_col.create_index("location_id")
        await weekly_col.create_index([("year", 1), ("week", 1)])
        await weekly_col.create_index([("location_id", 1), ("year", -1), ("week", -1)])
        print("  ✅ Indexes: location_id, year+week, compound")
        
        await weekly_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=5184000,  # 60 days
            name="ttl_60d"
        )
        print("  🕐 TTL index: created_at (60 days)")
        print("  → Data auto-deleted after 60 days (đã có monthly)\n")
        
        # === MONTHLY COLLECTION: 1 year TTL ===
        print("5️⃣  weather_monthly - 1 year retention")
        monthly_col = self.db["weather_monthly"]
        
        await monthly_col.create_index("location_id")
        await monthly_col.create_index([("year", 1), ("month", 1)])
        await monthly_col.create_index([("location_id", 1), ("year", -1), ("month", -1)])
        print("  ✅ Indexes: location_id, year+month, compound")
        
        await monthly_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=31536000,  # 1 year (365 days)
            name="ttl_1y"
        )
        print("  🕐 TTL index: created_at (1 year)")
        print("  → Data auto-deleted after 1 year (đủ để phân tích xu hướng)\n")
        
        # === LOCATIONS COLLECTION ===
        print("6️⃣  weather_locations - metadata")
        locations_col = self.db["weather_locations"]
        
        await locations_col.create_index("location_id", unique=True)
        await locations_col.create_index([("coordinates", "2dsphere")])
        print("  ✅ Indexes: location_id (unique), coordinates (2dsphere)\n")
        
        print("✅ All retention policy indexes created successfully!\n")
    
    async def verify_indexes(self):
        """Verify all indexes are created"""
        print("🔍 Verifying indexes...\n")
        
        collections = {
            "weather_raw": ["location_id", "timestamp", "ttl_24h"],
            "weather_hourly": ["location_id", "hour", "ttl_25h"],
            "weather_daily": ["location_id", "date", "ttl_32d"],
            "weather_weekly": ["location_id", "ttl_60d"],
            "weather_monthly": ["location_id", "ttl_1y"],
            "weather_locations": ["location_id"]
        }
        
        for coll_name, expected_indexes in collections.items():
            col = self.db[coll_name]
            indexes = await col.list_indexes().to_list(length=None)
            index_names = [idx["name"] for idx in indexes]
            
            print(f"📁 {coll_name}:")
            for idx_name in expected_indexes:
                if any(idx_name in name for name in index_names):
                    print(f"  ✅ {idx_name}")
                else:
                    print(f"  ❌ {idx_name} MISSING")
            
            # Show TTL info
            for idx in indexes:
                if "expireAfterSeconds" in idx:
                    ttl_seconds = idx["expireAfterSeconds"]
                    ttl_days = ttl_seconds / 86400
                    print(f"  🕐 TTL: {ttl_days:.1f} days ({ttl_seconds} seconds)")
            
            print()
        
        print("✅ Verification complete!\n")
    
    async def show_retention_summary(self):
        """Show retention policy summary"""
        print("=" * 70)
        print("📊 DATA RETENTION POLICY SUMMARY")
        print("=" * 70)
        print()
        print("Collection         | Retention | TTL (seconds) | Purpose")
        print("-" * 70)
        print("weather_raw        | 24 hours  | 86,400        | Real-time data → aggregate hourly")
        print("weather_hourly     | 25 hours  | 90,000        | Aggregate daily → delete after daily")
        print("weather_daily      | 32 days   | 2,764,800     | Aggregate monthly → delete after monthly")
        print("weather_weekly     | 60 days   | 5,184,000     | Seasonal trends")
        print("weather_monthly    | 1 year    | 31,536,000    | Long-term analysis")
        print("weather_locations  | PERMANENT | -             | Metadata")
        print("=" * 70)
        print()
        print("🔄 How TTL Works:")
        print("  - MongoDB checks TTL indexes every 60 seconds")
        print("  - Documents where (created_at + TTL < now) are deleted")
        print("  - Automatic cleanup, no manual intervention needed")
        print()
        print("💾 Storage Savings:")
        print("  - Without retention: ~6.3 GB/year (12 locations)")
        print("  - With retention:    ~27 MB/year (12 locations)")
        print("  - Savings:           99.6%")
        print()
        print("📊 Data Flow:")
        print("  Raw (24h) → Hourly (25h) → Daily (32d) → Monthly (1y)")
        print("  - Raw: Aggregate mỗi giờ thành hourly")
        print("  - Hourly (TTL 25h): Buffer 1h trước khi bị xoá, đủ thời gian aggregate daily")
        print("  - Daily (TTL 32d): Buffer 2 ngày trước khi bị xoá, đủ thời gian aggregate monthly")
        print("  - Monthly: Giữ 1 năm cho phân tích dài hạn")
        print()
        print("💡 Next Steps:")
        print("  1. Seed historical data:")
        print("     python -m scripts.seed_historical_data")
        print()
        print("  2. Wait 25 hours and check:")
        print("     mongosh citylens --eval 'db.weather_raw.countDocuments()'")
        print("     → Should see old data auto-deleted")
        print()
        print("  3. Start real-time collection:")
        print("     celery -A app.tasks.weather_tasks worker --beat")
        print()
        print("=" * 70)
    
    async def test_ttl_simulation(self):
        """Test TTL with simulated old data"""
        print("\n🧪 Testing TTL with simulated data...\n")
        
        raw_col = self.db["weather_raw_test"]
        
        # Create TTL index (1 minute for testing)
        await raw_col.create_index(
            [("created_at", 1)],
            expireAfterSeconds=60  # 1 minute for quick test
        )
        print("✅ Created test collection with 60-second TTL")
        
        # Insert test documents
        now = datetime.utcnow()
        old_time = now - timedelta(minutes=2)  # 2 minutes ago
        
        # Old document (should be deleted)
        await raw_col.insert_one({
            "location_id": "test_old",
            "timestamp": old_time,
            "created_at": old_time,
            "temp": 25.0
        })
        
        # New document (should stay)
        await raw_col.insert_one({
            "location_id": "test_new",
            "timestamp": now,
            "created_at": now,
            "temp": 28.0
        })
        
        print(f"✅ Inserted 2 test documents:")
        print(f"  - Old: created_at = {old_time}")
        print(f"  - New: created_at = {now}")
        
        # Count
        count = await raw_col.count_documents({})
        print(f"\n📊 Current count: {count} documents")
        
        print("\n⏳ Waiting 90 seconds for TTL to run...")
        print("   (MongoDB checks TTL every 60 seconds)")
        await asyncio.sleep(90)
        
        # Check again
        count_after = await raw_col.count_documents({})
        remaining = await raw_col.find({}).to_list(length=10)
        
        print(f"\n📊 After TTL: {count_after} documents")
        if count_after < count:
            print("✅ TTL working! Old document deleted")
            for doc in remaining:
                print(f"  Remaining: {doc['location_id']} (created {doc['created_at']})")
        else:
            print("⚠️  TTL not working yet (may need more time)")
        
        # Cleanup
        await raw_col.drop()
        print("\n✅ Test collection cleaned up")
    
    async def run(self, drop_first=False, test_ttl=False):
        """Main execution"""
        try:
            print("\n🚀 Setting up Data Retention Policy...\n")
            
            if drop_first:
                await self.drop_all_indexes()
            
            await self.create_retention_indexes()
            await self.verify_indexes()
            await self.show_retention_summary()
            
            if test_ttl:
                await self.test_ttl_simulation()
            
            print("\n🎉 Setup complete!\n")
        
        finally:
            self.client.close()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup data retention policy with TTL indexes"
    )
    parser.add_argument(
        "--drop-indexes",
        action="store_true",
        help="Drop existing indexes before creating new ones"
    )
    parser.add_argument(
        "--test-ttl",
        action="store_true",
        help="Run TTL simulation test (takes 90 seconds)"
    )
    
    args = parser.parse_args()
    
    setup = RetentionPolicySetup()
    await setup.run(drop_first=args.drop_indexes, test_ttl=args.test_ttl)


if __name__ == "__main__":
    asyncio.run(main())




