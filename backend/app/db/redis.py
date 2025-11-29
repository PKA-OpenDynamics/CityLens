# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Kết nối Redis
"""

import redis.asyncio as aioredis
from app.core.config import settings

redis_client = None


async def get_redis():
    """Lấy Redis connection"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def close_redis():
    """Đóng Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
