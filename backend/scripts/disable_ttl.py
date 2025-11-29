"""
Disable TTL indexes while keeping other indexes
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def disable_ttl():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB]
    
    collections = {
        "weather_raw": "ttl_24h",
        "weather_hourly": "ttl_1d",
        "weather_daily": "ttl_60d",
        "weather_weekly": "ttl_60d"
    }
    
    print("=" * 70)
    print("🛑 DISABLING TTL INDEXES")
    print("=" * 70)
    print("\n⚠️  This will disable automatic data cleanup")
    print("Storage will grow continuously without TTL.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Cancelled")
        return
    
    print()
    
    for col_name, index_name in collections.items():
        col = db[col_name]
        
        try:
            # Check if index exists
            indexes = await col.list_indexes().to_list(None)
            index_exists = any(idx["name"] == index_name for idx in indexes)
            
            if index_exists:
                await col.drop_index(index_name)
                print(f"✅ Dropped {col_name}.{index_name}")
            else:
                print(f"⏭️  {col_name}.{index_name} not found (already disabled)")
        
        except Exception as e:
            print(f"⚠️  {col_name}: {e}")
    
    print("\n✅ TTL disabled successfully!")
    print("💾 Data will be kept indefinitely")
    print("\n⚠️  Remember to manually clean up old data periodically")
    print("=" * 70)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(disable_ttl())





