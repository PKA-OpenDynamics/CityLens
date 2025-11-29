# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather & Air Quality API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.db.mongodb import get_mongodb
from app.db.redis import get_redis

logger = logging.getLogger(__name__)
from app.services.weather_service import WeatherService, collect_weather_data_for_location
from app.services.weather_aggregation import WeatherAggregationService
from app.services.realtime_weather_service import RealtimeWeatherService
from app.services.forecast_service import ForecastService
from app.models.weather import (
    WeatherLocation, WeatherRaw, WeatherHourly, WeatherDaily, WeatherMonthly,
    WeatherForecast, RealtimeWeatherResponse, RealtimeWeatherSummaryResponse
)

router = APIRouter()


@router.get("/locations", response_model=List[WeatherLocation])
async def get_weather_locations(
    active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get all weather monitoring locations"""
    service = WeatherService(db)
    
    if active is not None:
        cursor = db["weather_locations"].find({"active": active})
    else:
        cursor = db["weather_locations"].find()
    
    locations = []
    async for doc in cursor:
        # Convert _id to string if present
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        locations.append(WeatherLocation(**doc))
    
    return locations


@router.get("/locations/{location_id}", response_model=WeatherLocation)
async def get_weather_location(
    location_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get a specific weather location"""
    service = WeatherService(db)
    location = await service.get_location(location_id)
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Ensure _id is converted to string if present
    if hasattr(location, 'id') and location.id:
        location.id = str(location.id)
    
    return location


@router.get("/locations/{location_id}/latest", response_model=Optional[WeatherRaw])
async def get_latest_weather(
    location_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get latest weather data for a location"""
    service = WeatherService(db)
    data = await service.get_latest_data(location_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this location")
    
    return data


@router.get("/locations/{location_id}/hourly", response_model=List[WeatherHourly])
async def get_hourly_weather(
    location_id: str,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to retrieve (max 7 days)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get hourly weather data for a location"""
    service = WeatherService(db)
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    data = await service.get_hourly_data(location_id, start_time, end_time)
    
    return data


@router.get("/locations/{location_id}/daily", response_model=List[WeatherDaily])
async def get_daily_weather(
    location_id: str,
    days: int = Query(7, ge=1, le=90, description="Number of days to retrieve (max 90 days)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get daily weather data for a location"""
    service = WeatherService(db)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    data = await service.get_daily_data(location_id, start_date, end_date)
    
    return data


@router.get("/locations/{location_id}/monthly", response_model=List[WeatherMonthly])
async def get_monthly_weather(
    location_id: str,
    year: Optional[int] = Query(None, description="Year to retrieve (default: all)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get monthly weather data for a location"""
    service = WeatherService(db)
    
    data = await service.get_monthly_data(location_id, year)
    
    return data


@router.get("/nearby")
async def get_nearby_locations(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: int = Query(10000, ge=1000, le=50000, description="Radius in meters (1-50km)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Find weather locations near a point"""
    service = WeatherService(db)
    
    locations = await service.find_nearby_locations(lon, lat, radius)
    
    return locations


@router.post("/locations/{location_id}/collect")
async def trigger_data_collection(
    location_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Manually trigger data collection for a location (admin only)"""
    service = WeatherService(db)
    
    location = await service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    success = await collect_weather_data_for_location(db, location)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to collect data")
    
    return {"status": "success", "message": "Data collection triggered"}


@router.post("/locations/{location_id}/aggregate/hourly")
async def trigger_hourly_aggregation(
    location_id: str,
    hours_back: int = Query(24, ge=1, le=168),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Manually trigger hourly aggregation for a location (admin only)"""
    service = WeatherAggregationService(db)
    
    from app.services.weather_aggregation import round_to_hour
    
    now = datetime.utcnow()
    for i in range(hours_back):
        hour = round_to_hour(now - timedelta(hours=i))
        await service.aggregate_hourly(location_id, hour)
    
    return {"status": "success", "message": f"Aggregated {hours_back} hours"}


@router.post("/locations/{location_id}/aggregate/daily")
async def trigger_daily_aggregation(
    location_id: str,
    days_back: int = Query(7, ge=1, le=90),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Manually trigger daily aggregation for a location (admin only)"""
    service = WeatherAggregationService(db)
    
    from app.services.weather_aggregation import round_to_day
    
    now = datetime.utcnow()
    for i in range(days_back):
        date = round_to_day(now - timedelta(days=i))
        await service.aggregate_daily(location_id, date)
    
    return {"status": "success", "message": f"Aggregated {days_back} days"}


@router.get("/stats/summary")
async def get_stats_summary(
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Get overall statistics summary"""
    
    total_locations = await db["weather_locations"].count_documents({"active": True})
    total_raw_records = await db["weather_raw"].count_documents({})
    total_hourly_records = await db["weather_hourly"].count_documents({})
    total_daily_records = await db["weather_daily"].count_documents({})
    total_monthly_records = await db["weather_monthly"].count_documents({})
    
    # Get latest measurement time
    latest_doc = await db["weather_raw"].find_one(sort=[("timestamp", -1)])
    latest_measurement = latest_doc.get("timestamp") if latest_doc else None
    
    return {
        "total_locations": total_locations,
        "total_raw_records": total_raw_records,
        "total_hourly_records": total_hourly_records,
        "total_daily_records": total_daily_records,
        "total_monthly_records": total_monthly_records,
        "latest_measurement": latest_measurement
    }


@router.get("/health")
async def weather_health_check(
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """Health check for weather data system"""
    
    # Check if we have recent data (within last hour)
    cutoff = datetime.utcnow() - timedelta(hours=1)
    recent_count = await db["weather_raw"].count_documents({"timestamp": {"$gte": cutoff}})
    
    is_healthy = recent_count > 0
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "recent_measurements": recent_count,
        "last_check": datetime.utcnow().isoformat()
    }


# === Real-time Weather Endpoints ===

@router.get("/realtime/{location_id}", response_model=RealtimeWeatherResponse)
async def get_realtime_weather(
    location_id: str,
    use_cache: bool = Query(True, description="Use Redis cache"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get real-time weather and air quality data for a location
    
    - Uses Redis cache for fast response (5 min TTL)
    - Returns latest data with freshness indicator
    - Optimized for mobile/web apps
    """
    try:
        redis_client = await get_redis()
    except Exception as e:
        # If Redis is not available, continue without cache
        logger.warning(f"Redis not available: {e}")
        redis_client = None
    
    service = RealtimeWeatherService(db, redis_client)
    
    data = await service.get_realtime_data(location_id, use_cache=use_cache)
    
    if not data:
        raise HTTPException(status_code=404, detail="No real-time data found for this location")
    
    return data


@router.get("/realtime", response_model=RealtimeWeatherSummaryResponse)
async def get_realtime_summary(
    active_only: bool = Query(True, description="Only active locations"),
    use_cache: bool = Query(True, description="Use Redis cache"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get real-time weather summary for all locations
    
    - Returns cached summary for fast response
    - Includes all active locations with latest data
    - Perfect for dashboard/homepage
    """
    try:
        redis_client = await get_redis()
    except Exception as e:
        # If Redis is not available, continue without cache
        logger.warning(f"Redis not available: {e}")
        redis_client = None
    
    try:
        service = RealtimeWeatherService(db, redis_client)
        summary = await service.get_realtime_summary(active_only=active_only, use_cache=use_cache)
        return summary
    except Exception as e:
        logger.error(f"Error getting realtime summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching real-time data: {str(e)}")


@router.get("/realtime/nearby", response_model=List[RealtimeWeatherResponse])
async def get_nearby_realtime(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: int = Query(10000, ge=1000, le=50000, description="Radius in meters"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get real-time weather data for locations near a point
    
    - Useful for location-based apps
    - Returns nearest locations with real-time data
    """
    try:
        redis_client = await get_redis()
    except Exception as e:
        # If Redis is not available, continue without cache
        logger.warning(f"Redis not available: {e}")
        redis_client = None
    
    service = RealtimeWeatherService(db, redis_client)
    
    results = await service.get_nearby_realtime(lat, lon, radius, limit)
    return results


# === Forecast Endpoints ===

@router.get("/forecast/{location_id}", response_model=WeatherForecast)
async def get_weather_forecast(
    location_id: str,
    days: int = Query(5, ge=1, le=5, description="Number of days (max 5)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Get 5-day weather and air quality forecast for a location
    
    - Returns forecast with 3-hour intervals
    - Includes weather and air quality predictions
    - Forecast is updated 2-3 times per day
    """
    service = ForecastService(db)
    
    forecast = await service.get_forecast(location_id, days=days)
    
    if not forecast:
        raise HTTPException(
            status_code=404,
            detail="No forecast found for this location. Forecast may not be available yet."
        )
    
    return forecast


@router.post("/forecast/{location_id}/refresh")
async def refresh_forecast(
    location_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb)
):
    """
    Manually trigger forecast refresh for a location (admin only)
    
    - Fetches latest forecast from OpenWeatherMap
    - Updates database with new forecast data
    """
    weather_service = WeatherService(db)
    forecast_service = ForecastService(db)
    
    location = await weather_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    success = await forecast_service.fetch_and_save_forecast(
        location.location_id,
        location.name,
        location.location
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to fetch forecast")
    
    return {
        "status": "success",
        "message": "Forecast refreshed successfully",
        "location_id": location_id
    }






