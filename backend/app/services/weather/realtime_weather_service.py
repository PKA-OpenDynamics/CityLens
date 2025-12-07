# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Real-time Weather Data Service with Redis Caching
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as aioredis

from app.models.weather import (
    RealtimeWeatherResponse, RealtimeWeatherSummaryResponse,
    WeatherRaw, WeatherLocation
)
from app.services.weather.weather_service import WeatherService

logger = logging.getLogger(__name__)


class RealtimeWeatherService:
    """Service for real-time weather data with Redis caching"""
    
    # Cache TTL: 5 minutes (data is refreshed every 10 minutes)
    CACHE_TTL_SECONDS = 300
    
    def __init__(self, db: AsyncIOMotorDatabase, redis_client: Optional[aioredis.Redis] = None):
        self.db = db
        self.redis = redis_client
        self.weather_service = WeatherService(db)
    
    def _get_cache_key(self, location_id: str) -> str:
        """Generate Redis cache key for location"""
        return f"weather:realtime:{location_id}"
    
    def _get_summary_cache_key(self) -> str:
        """Generate Redis cache key for summary"""
        return "weather:realtime:summary"
    
    async def get_realtime_data(
        self,
        location_id: str,
        use_cache: bool = True
    ) -> Optional[RealtimeWeatherResponse]:
        """
        Get real-time weather data for a location
        
        Args:
            location_id: Location identifier
            use_cache: Whether to use Redis cache (default True)
        
        Returns:
            RealtimeWeatherResponse or None
        """
        # Try cache first
        if use_cache and self.redis:
            try:
                cached = await self.redis.get(self._get_cache_key(location_id))
                if cached:
                    data = json.loads(cached)
                    # Parse datetime strings
                    data["timestamp"] = datetime.fromisoformat(data["timestamp"])
                    if data.get("weather"):
                        data["weather"] = data["weather"]  # Already dict
                    if data.get("air_quality"):
                        data["air_quality"] = data["air_quality"]  # Already dict
                    return RealtimeWeatherResponse(**data)
            except Exception as e:
                logger.warning(f"Error reading from cache: {e}")
                # Continue without cache if Redis fails
        
        # Get from database
        raw_data = await self.weather_service.get_latest_data(location_id)
        if not raw_data:
            return None
        
        # Get location info
        location = await self.weather_service.get_location(location_id)
        if not location:
            return None
        
        # Calculate data age
        now = datetime.utcnow()
        data_age = (now - raw_data.timestamp).total_seconds()
        is_fresh = data_age < 600  # < 10 minutes
        
        # Build response
        response = RealtimeWeatherResponse(
            location_id=location_id,
            location_name=location.name,
            timestamp=raw_data.timestamp,
            weather=raw_data.weather,
            air_quality=raw_data.air_quality,
            data_age_seconds=int(data_age),
            is_fresh=is_fresh,
            sources=[raw_data.source] if raw_data.source else []
        )
        
        # Cache the response
        if use_cache and self.redis:
            try:
                cache_data = response.model_dump(mode="json")
                # model_dump(mode="json") already converts datetime to ISO string
                await self.redis.setex(
                    self._get_cache_key(location_id),
                    self.CACHE_TTL_SECONDS,
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Error writing to cache: {e}")
        
        return response
    
    async def get_realtime_summary(
        self,
        active_only: bool = True,
        use_cache: bool = True
    ) -> RealtimeWeatherSummaryResponse:
        """
        Get real-time weather summary for all locations
        
        Args:
            active_only: Only include active locations
            use_cache: Whether to use Redis cache
        
        Returns:
            RealtimeWeatherSummaryResponse
        """
        # Try cache first
        if use_cache and self.redis:
            try:
                cached = await self.redis.get(self._get_summary_cache_key())
                if cached:
                    data = json.loads(cached)
                    # Parse datetimes
                    data["generated_at"] = datetime.fromisoformat(data["generated_at"])
                    for loc in data["locations"]:
                        loc["timestamp"] = datetime.fromisoformat(loc["timestamp"])
                    return RealtimeWeatherSummaryResponse(**data)
            except Exception as e:
                logger.warning(f"Error reading summary from cache: {e}")
                # Continue without cache if Redis fails
        
        # Get all active locations
        if active_only:
            try:
                locations = await self.weather_service.get_all_active_locations()
            except Exception as e:
                logger.error(f"Error getting active locations: {e}", exc_info=True)
                locations = []
        else:
            # Get all locations (active and inactive)
            cursor = self.db["weather_locations"].find()
            locations = []
            async for doc in cursor:
                # Convert _id to string if present
                if "_id" in doc:
                    doc["id"] = str(doc["_id"])
                try:
                    locations.append(WeatherLocation(**doc))
                except Exception as e:
                    logger.warning(f"Error parsing location {doc.get('_id')}: {e}")
                    continue
        
        if not locations:
            logger.warning("No locations found in database")
            # Return empty summary instead of error
            return RealtimeWeatherSummaryResponse(
                locations=[],
                generated_at=datetime.utcnow(),
                total_locations=0
            )
        
        # Get real-time data for each location
        realtime_data = []
        for location in locations:
            try:
                data = await self.get_realtime_data(location.location_id, use_cache=False)
                if data:
                    realtime_data.append(data)
            except Exception as e:
                logger.warning(f"Error getting realtime data for {location.location_id}: {e}")
                continue
        
        # Build summary
        summary = RealtimeWeatherSummaryResponse(
            locations=realtime_data,
            generated_at=datetime.utcnow(),
            total_locations=len(realtime_data)
        )
        
        # Cache the summary
        if use_cache and self.redis:
            try:
                cache_data = summary.model_dump(mode="json")
                # model_dump(mode="json") already converts datetime to ISO string
                await self.redis.setex(
                    self._get_summary_cache_key(),
                    self.CACHE_TTL_SECONDS,
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Error writing summary to cache: {e}")
        
        return summary
    
    async def get_nearby_realtime(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
        limit: int = 10
    ) -> List[RealtimeWeatherResponse]:
        """
        Get real-time data for locations near a point
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters
            limit: Maximum number of results
        
        Returns:
            List of RealtimeWeatherResponse
        """
        # Find nearby locations
        locations = await self.weather_service.find_nearby_locations(lon, lat, radius)
        
        # Get real-time data for each
        results = []
        for location in locations[:limit]:
            data = await self.get_realtime_data(location.location_id)
            if data:
                results.append(data)
        
        return results
    
    async def invalidate_cache(self, location_id: Optional[str] = None):
        """
        Invalidate cache for a location or all locations
        
        Args:
            location_id: Location to invalidate (None = all)
        """
        if not self.redis:
            return
        
        try:
            if location_id:
                await self.redis.delete(self._get_cache_key(location_id))
            else:
                # Delete all realtime cache keys
                pattern = "weather:realtime:*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")



