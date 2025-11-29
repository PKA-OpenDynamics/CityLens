# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Forecast Data Service
"""

import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.weather import WeatherForecast, WeatherForecastPoint, AirQualityForecastPoint, GeoLocation
from app.services.weather_api import openweather_client

logger = logging.getLogger(__name__)


class ForecastService:
    """Service for weather forecast operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.forecast_col = db["weather_forecast"]
    
    async def initialize_indexes(self):
        """Create necessary indexes for forecast collection"""
        try:
            await self.forecast_col.create_index([("location_id", 1), ("valid_until", -1)])
            await self.forecast_col.create_index([("location", "2dsphere")])
            await self.forecast_col.create_index("generated_at")
            await self.forecast_col.create_index("valid_until")
            # No TTL index needed: We UPDATE (overwrite) forecast every 6 hours via Celery.
            # Document always contains only the latest 5 days, so no stale data accumulates.
            # If fetch fails, next successful fetch will overwrite anyway.
            logger.info("Forecast database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating forecast indexes: {e}")
    
    async def fetch_and_save_forecast(
        self,
        location_id: str,
        location_name: str,
        location: GeoLocation
    ) -> bool:
        """
        Fetch forecast from OpenWeatherMap and save to database
        
        Args:
            location_id: Location identifier
            location_name: Location name
            location: GeoLocation object
        
        Returns:
            True if successful
        """
        try:
            lat = location.coordinates[1]
            lon = location.coordinates[0]
            
            # Fetch weather forecast (5 days, 3-hour intervals)
            weather_forecast_data = await self._fetch_weather_forecast(lat, lon)
            if not weather_forecast_data:
                logger.warning(f"No weather forecast data for {location_id}")
                return False
            
            # Fetch air quality forecast
            air_forecast_data = await self._fetch_air_quality_forecast(lat, lon)
            
            # Parse and merge forecasts
            weather_points = self._parse_weather_forecast(weather_forecast_data)
            air_points = self._parse_air_quality_forecast(air_forecast_data) if air_forecast_data else []
            
            # Calculate validity (5 days from now)
            now = datetime.utcnow()
            valid_until = now + timedelta(days=5)
            
            # Create forecast document
            forecast = WeatherForecast(
                location_id=location_id,
                location_name=location_name,
                location=location,
                weather_forecasts=weather_points,
                air_quality_forecasts=air_points,
                generated_at=now,
                valid_until=valid_until
            )
            
            # Upsert (replace existing forecast for this location)
            # This will overwrite old forecast data for overlapping days
            await self.forecast_col.update_one(
                {"location_id": location_id},
                {"$set": forecast.model_dump(by_alias=True, exclude={"id"})},
                upsert=True
            )
            
            logger.info(f"Saved forecast for {location_id} ({len(weather_points)} weather points, {len(air_points)} air quality points)")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching/saving forecast for {location_id}: {e}")
            return False
    
    async def _fetch_weather_forecast(self, lat: float, lon: float) -> Optional[dict]:
        """Fetch 5-day weather forecast from OpenWeatherMap"""
        try:
            url = f"{openweather_client.BASE_URL}/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": openweather_client.api_key,
                "units": "metric"
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return None
    
    async def _fetch_air_quality_forecast(self, lat: float, lon: float) -> Optional[dict]:
        """Fetch 5-day air quality forecast from OpenWeatherMap"""
        try:
            url = f"{openweather_client.BASE_URL}/air_pollution/forecast"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": openweather_client.api_key
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching air quality forecast: {e}")
            return None
    
    def _parse_weather_forecast(self, data: dict) -> List[WeatherForecastPoint]:
        """Parse OpenWeatherMap forecast response"""
        points = []
        try:
            for item in data.get("list", []):
                main = item.get("main", {})
                wind = item.get("wind", {})
                clouds = item.get("clouds", {})
                rain = item.get("rain", {})
                weather = item.get("weather", [{}])[0]
                
                point = WeatherForecastPoint(
                    timestamp=datetime.fromtimestamp(item["dt"]),
                    temp=main.get("temp"),
                    temp_min=main.get("temp_min"),
                    temp_max=main.get("temp_max"),
                    humidity=main.get("humidity"),
                    pressure=main.get("pressure"),
                    wind_speed=wind.get("speed"),
                    wind_deg=wind.get("deg"),
                    clouds=clouds.get("all"),
                    rain_3h=rain.get("3h", 0.0),
                    condition=weather.get("main"),
                    visibility=item.get("visibility")
                )
                points.append(point)
        except Exception as e:
            logger.error(f"Error parsing weather forecast: {e}")
        
        return points
    
    def _parse_air_quality_forecast(self, data: dict) -> List[AirQualityForecastPoint]:
        """Parse OpenWeatherMap air quality forecast response"""
        points = []
        try:
            for item in data.get("list", []):
                components = item.get("components", {})
                main = item.get("main", {})
                
                point = AirQualityForecastPoint(
                    timestamp=datetime.fromtimestamp(item["dt"]),
                    aqi=main.get("aqi"),
                    pm2_5=components.get("pm2_5"),
                    pm10=components.get("pm10"),
                    co=components.get("co"),
                    no2=components.get("no2"),
                    o3=components.get("o3"),
                    so2=components.get("so2")
                )
                points.append(point)
        except Exception as e:
            logger.error(f"Error parsing air quality forecast: {e}")
        
        return points
    
    async def get_forecast(
        self,
        location_id: str,
        days: int = 5
    ) -> Optional[WeatherForecast]:
        """
        Get forecast for a location
        
        Args:
            location_id: Location identifier
            days: Number of days to retrieve (default 5, max 5)
        
        Returns:
            WeatherForecast or None
        """
        # Get latest forecast
        doc = await self.forecast_col.find_one(
            {"location_id": location_id},
            sort=[("generated_at", -1)]
        )
        
        if not doc:
            return None
        
        forecast = WeatherForecast(**doc)
        
        # Filter by days if needed
        if days < 5:
            cutoff_time = datetime.utcnow() + timedelta(days=days)
            forecast.weather_forecasts = [
                f for f in forecast.weather_forecasts
                if f.timestamp <= cutoff_time
            ]
            forecast.air_quality_forecasts = [
                f for f in forecast.air_quality_forecasts
                if f.timestamp <= cutoff_time
            ]
        
        return forecast
    
    async def get_all_forecasts(self) -> List[WeatherForecast]:
        """Get all active forecasts"""
        # Get forecasts that are still valid
        now = datetime.utcnow()
        cursor = self.forecast_col.find(
            {"valid_until": {"$gt": now}}
        ).sort("location_id", 1)
        
        forecasts = []
        async for doc in cursor:
            forecasts.append(WeatherForecast(**doc))
        
        return forecasts

