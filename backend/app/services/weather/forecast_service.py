# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Forecast Data Service
"""

import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.weather import (
    WeatherForecast, WeatherForecastPoint, AirQualityForecastPoint, 
    GeoLocation, DailyForecast, DailyForecastDocument,
    ForecastHourly, ForecastDailySummary
)
from app.services.weather.weather_api import openweather_client

logger = logging.getLogger(__name__)


class ForecastService:
    """Service for weather forecast operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Legacy collections (for backward compatibility)
        self.forecast_col = db["weather_forecast"]  # Legacy: 1 document per location
        self.forecast_daily_col = db["weather_forecast_daily"]  # Legacy: 1 document per day
        
        # Simplified hybrid structure (recommended) - Only 2 collections
        self.forecast_hourly_col = db["forecast_hourly"]  # 1 document per hour (weather + air quality)
        self.forecast_daily_summary_col = db["forecast_daily_summary"]  # 1 document per day (summary only)
    
    async def initialize_indexes(self):
        """Create necessary indexes for forecast collections"""
        try:
            # Legacy collection (1 document per location)
            await self.forecast_col.create_index([("location_id", 1), ("valid_until", -1)])
            await self.forecast_col.create_index([("location", "2dsphere")])
            await self.forecast_col.create_index("generated_at")
            await self.forecast_col.create_index("valid_until")
            
            # Legacy collection (1 document per day)
            await self.forecast_daily_col.create_index([("location_id", 1), ("date", 1)], unique=True)
            await self.forecast_daily_col.create_index([("location_id", 1), ("date", -1)])
            await self.forecast_daily_col.create_index([("location", "2dsphere")])
            await self.forecast_daily_col.create_index("date")
            await self.forecast_daily_col.create_index("valid_until")
            
            # Simplified hybrid structure - Hourly forecast (weather + air quality in 1 document, TTL 72h)
            await self.forecast_hourly_col.create_index([("location_id", 1), ("timestamp", 1)], unique=True)
            await self.forecast_hourly_col.create_index([("location_id", 1), ("timestamp", -1)])
            await self.forecast_hourly_col.create_index([("location", "2dsphere")])
            await self.forecast_hourly_col.create_index("timestamp")
            await self.forecast_hourly_col.create_index([("valid_until", 1)], expireAfterSeconds=259200)  # 72h TTL
            
            # Simplified hybrid structure - Daily summary (computed statistics, TTL 10 days)
            await self.forecast_daily_summary_col.create_index([("location_id", 1), ("date", 1)], unique=True)
            await self.forecast_daily_summary_col.create_index([("location_id", 1), ("date", -1)])
            await self.forecast_daily_summary_col.create_index([("location", "2dsphere")])
            await self.forecast_daily_summary_col.create_index("date")
            await self.forecast_daily_summary_col.create_index([("valid_until", 1)], expireAfterSeconds=864000)  # 10 days TTL
            
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
            
            # === SIMPLIFIED HYBRID STRUCTURE: Weather + Air Quality in 1 document ===
            # Both use same 3-hour intervals from OpenWeatherMap
            
            # 1. Match air quality to weather timestamps (same 3-hour intervals)
            # Create a map of air quality by timestamp for quick lookup
            air_by_timestamp = {point.timestamp: point for point in air_points}
            
            # 2. Save hourly forecasts (weather + air quality in 1 document)
            saved_hourly = 0
            
            for weather_point in weather_points:
                # Find matching air quality (same timestamp or closest)
                air_point = air_by_timestamp.get(weather_point.timestamp)
                
                # If no exact match, find closest (within 1 hour)
                if not air_point:
                    for air_ts, air_pt in air_by_timestamp.items():
                        time_diff = abs((weather_point.timestamp - air_ts).total_seconds())
                        if time_diff < 3600:  # Within 1 hour
                            air_point = air_pt
                            break
                
                # Create combined hourly forecast
                hourly_forecast = ForecastHourly(
                    location_id=location_id,
                    location_name=location_name,
                    location=location,
                    timestamp=weather_point.timestamp,
                    # Weather data
                    temp=weather_point.temp,
                    temp_min=weather_point.temp_min,
                    temp_max=weather_point.temp_max,
                    humidity=weather_point.humidity,
                    pressure=weather_point.pressure,
                    wind_speed=weather_point.wind_speed,
                    wind_deg=weather_point.wind_deg,
                    clouds=weather_point.clouds,
                    rain_3h=weather_point.rain_3h,
                    condition=weather_point.condition,
                    visibility=weather_point.visibility,
                    # Air quality data (if available)
                    aqi=air_point.aqi if air_point else None,
                    pm2_5=air_point.pm2_5 if air_point else None,
                    pm10=air_point.pm10 if air_point else None,
                    co=air_point.co if air_point else None,
                    no2=air_point.no2 if air_point else None,
                    o3=air_point.o3 if air_point else None,
                    so2=air_point.so2 if air_point else None,
                    generated_at=now,
                    valid_until=valid_until
                )
                
                # Save to hourly collection
                hourly_dict = hourly_forecast.model_dump(by_alias=True, exclude={"id"})
                await self.forecast_hourly_col.update_one(
                    {"location_id": location_id, "timestamp": weather_point.timestamp},
                    {"$set": hourly_dict},
                    upsert=True
                )
                saved_hourly += 1
            
            # 3. Organize by days and save daily summaries (computed from hourly)
            daily_forecasts = self._organize_by_days(weather_points, air_points)
            saved_daily_summaries = 0
            for daily in daily_forecasts:
                summary = self._compute_daily_summary(daily.weather_forecasts, daily.air_quality_forecasts)
                
                daily_summary = ForecastDailySummary(
                    location_id=location_id,
                    location_name=location_name,
                    location=location,
                    date=daily.date,
                    temp_min=summary.get("temp_min"),
                    temp_max=summary.get("temp_max"),
                    temp_avg=summary.get("temp_avg"),
                    condition=summary.get("condition"),
                    rain_total=summary.get("rain_total"),
                    has_rain=summary.get("has_rain", False),
                    aqi_min=summary.get("aqi_min"),
                    aqi_max=summary.get("aqi_max"),
                    aqi_avg=summary.get("aqi_avg"),
                    pm2_5_avg=summary.get("pm2_5_avg"),
                    generated_at=now,
                    valid_until=valid_until
                )
                
                summary_dict = daily_summary.model_dump(by_alias=True, exclude={"id"})
                await self.forecast_daily_summary_col.update_one(
                    {"location_id": location_id, "date": daily.date},
                    {"$set": summary_dict},
                    upsert=True
                )
                saved_daily_summaries += 1
            
            # === LEGACY: Also save old format for backward compatibility ===
            saved_days = 0
            for daily in daily_forecasts:
                summary = self._compute_daily_summary(daily.weather_forecasts, daily.air_quality_forecasts)
                daily_doc = DailyForecastDocument(
                    location_id=location_id,
                    location_name=location_name,
                    location=location,
                    date=daily.date,
                    weather=daily.weather_forecasts,
                    air_quality=daily.air_quality_forecasts,
                    summary=summary,
                    generated_at=now,
                    valid_until=valid_until
                )
                daily_dict = daily_doc.model_dump(by_alias=True, exclude={"id"})
                await self.forecast_daily_col.update_one(
                    {"location_id": location_id, "date": daily.date},
                    {"$set": daily_dict},
                    upsert=True
                )
                saved_days += 1
            
            # Also save legacy format for backward compatibility (1 document per location)
            forecast = WeatherForecast(
                location_id=location_id,
                location_name=location_name,
                location=location,
                days=daily_forecasts,
                generated_at=now,
                valid_until=valid_until
            )
            forecast_dict = forecast.model_dump(by_alias=True, exclude={"id"})
            # Remove old flat arrays if they exist
            forecast_dict.pop("weather_forecasts", None)
            forecast_dict.pop("air_quality_forecasts", None)
            await self.forecast_col.update_one(
                {"location_id": location_id},
                {"$set": forecast_dict},
                upsert=True
            )
            
            logger.info(
                f"Saved forecast for {location_id} - "
                f"Hourly: {saved_hourly} documents (weather+AQ), "
                f"Daily summaries: {saved_daily_summaries} days"
            )
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
    
    def _organize_by_days(
        self,
        weather_points: List[WeatherForecastPoint],
        air_points: List[AirQualityForecastPoint]
    ) -> List[DailyForecast]:
        """
        Organize forecast points by days for easier querying and display
        
        Groups weather and air quality forecasts by date (YYYY-MM-DD)
        Similar structure to raw data - simple and meaningful
        """
        from collections import defaultdict
        
        # Group weather points by date
        weather_by_date = defaultdict(list)
        for point in weather_points:
            date_key = point.timestamp.strftime("%Y-%m-%d")
            weather_by_date[date_key].append(point)
        
        # Group air quality points by date
        air_by_date = defaultdict(list)
        for point in air_points:
            date_key = point.timestamp.strftime("%Y-%m-%d")
            air_by_date[date_key].append(point)
        
        # Get all unique dates and sort them
        all_dates = sorted(set(list(weather_by_date.keys()) + list(air_by_date.keys())))
        
        # Create DailyForecast for each date
        daily_forecasts = []
        for date_str in all_dates:
            daily = DailyForecast(
                date=date_str,
                weather_forecasts=weather_by_date.get(date_str, []),
                air_quality_forecasts=air_by_date.get(date_str, [])
            )
            daily_forecasts.append(daily)
        
        return daily_forecasts
    
    def _compute_daily_summary(
        self,
        weather_points: List[WeatherForecastPoint],
        air_points: List[AirQualityForecastPoint]
    ) -> Dict[str, Any]:
        """Compute daily summary from forecast points"""
        summary = {}
        
        if weather_points:
            temps = [p.temp for p in weather_points if p.temp is not None]
            if temps:
                summary["temp_min"] = min(temps)
                summary["temp_max"] = max(temps)
                summary["temp_avg"] = sum(temps) / len(temps)
            
            # Most common condition
            conditions = [p.condition for p in weather_points if p.condition]
            if conditions:
                from collections import Counter
                summary["condition"] = Counter(conditions).most_common(1)[0][0]
            
            # Rain
            rain_total = sum(p.rain_3h or 0 for p in weather_points)
            summary["rain_total"] = rain_total
            summary["has_rain"] = rain_total > 0
        
        if air_points:
            aqis = [p.aqi for p in air_points if p.aqi is not None]
            if aqis:
                summary["aqi_min"] = min(aqis)
                summary["aqi_max"] = max(aqis)
                summary["aqi_avg"] = sum(aqis) / len(aqis)
            
            pm25_values = [p.pm2_5 for p in air_points if p.pm2_5 is not None]
            if pm25_values:
                summary["pm2_5_avg"] = sum(pm25_values) / len(pm25_values)
        
        return summary
    
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
        # Try new simplified structure (forecast_hourly - weather + air quality in 1 document)
        now = datetime.utcnow()
        cutoff_time = now + timedelta(days=days)
        
        # Get hourly forecasts (weather + air quality combined)
        cursor = self.forecast_hourly_col.find(
            {
                "location_id": location_id,
                "timestamp": {"$lte": cutoff_time},
                "valid_until": {"$gt": now}
            }
        ).sort("timestamp", 1)
        
        hourly_docs = await cursor.to_list(length=None)
        
        if hourly_docs:
            # Get location info from first document
            location_name = hourly_docs[0].get("location_name", "")
            location_data = hourly_docs[0].get("location", {})
            generated_at = hourly_docs[0].get("generated_at", now)
            valid_until = hourly_docs[0].get("valid_until", now + timedelta(days=5))
            
            # Convert to WeatherForecastPoint and AirQualityForecastPoint
            weather_points = []
            air_points = []
            
            for doc in hourly_docs:
                if "_id" in doc:
                    doc.pop("_id")
                
                # Weather point
                weather_point = WeatherForecastPoint(
                    timestamp=doc["timestamp"],
                    temp=doc.get("temp"),
                    temp_min=doc.get("temp_min"),
                    temp_max=doc.get("temp_max"),
                    humidity=doc.get("humidity"),
                    pressure=doc.get("pressure"),
                    wind_speed=doc.get("wind_speed"),
                    wind_deg=doc.get("wind_deg"),
                    clouds=doc.get("clouds"),
                    rain_3h=doc.get("rain_3h"),
                    condition=doc.get("condition"),
                    visibility=doc.get("visibility")
                )
                weather_points.append(weather_point)
                
                # Air quality point (same timestamp)
                if doc.get("aqi") is not None or doc.get("pm2_5") is not None:
                    air_point = AirQualityForecastPoint(
                        timestamp=doc["timestamp"],
                        aqi=doc.get("aqi"),
                        pm2_5=doc.get("pm2_5"),
                        pm10=doc.get("pm10"),
                        co=doc.get("co"),
                        no2=doc.get("no2"),
                        o3=doc.get("o3"),
                        so2=doc.get("so2")
                    )
                    air_points.append(air_point)
            
            # Organize by days
            daily_forecasts = self._organize_by_days(weather_points, air_points)
            
            days_list = []
            for daily in daily_forecasts:
                days_list.append(daily)
            
            forecast = WeatherForecast(
                location_id=location_id,
                location_name=location_name,
                location=GeoLocation(**location_data),
                days=days_list,
                generated_at=generated_at,
                valid_until=valid_until
            )
            return forecast
        
        # Fallback to legacy structure (1 document per day)
        cutoff_date = cutoff_time.strftime("%Y-%m-%d")
        cursor = self.forecast_daily_col.find(
            {
                "location_id": location_id,
                "date": {"$lte": cutoff_date},
                "valid_until": {"$gt": now}
            }
        ).sort("date", 1).limit(days)
        
        daily_docs = await cursor.to_list(length=days)
        
        if daily_docs:
            # Convert to WeatherForecast format
            location_name = daily_docs[0].get("location_name", "")
            location_data = daily_docs[0].get("location", {})
            generated_at = daily_docs[0].get("generated_at", now)
            valid_until = daily_docs[0].get("valid_until", now + timedelta(days=5))
            
            days_list = []
            for doc in daily_docs:
                if "_id" in doc:
                    doc.pop("_id")
                
                daily = DailyForecast(
                    date=doc["date"],
                    weather_forecasts=doc.get("weather", []),
                    air_quality_forecasts=doc.get("air_quality", [])
                )
                days_list.append(daily)
            
            forecast = WeatherForecast(
                location_id=location_id,
                location_name=location_name,
                location=GeoLocation(**location_data),
                days=days_list,
                generated_at=generated_at,
                valid_until=valid_until
            )
            return forecast
        
        # Fallback to legacy format (1 document per location)
        doc = await self.forecast_col.find_one(
            {"location_id": location_id},
            sort=[("generated_at", -1)]
        )
        
        if not doc:
            return None
        
        # Convert _id to string if present
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        
        # Normalize location if needed
        if "location" in doc and isinstance(doc["location"], dict):
            # Ensure location is in correct format
            if "coordinates" in doc["location"] and isinstance(doc["location"]["coordinates"], list):
                # Already in correct format
                pass
            elif "type" not in doc["location"]:
                doc["location"]["type"] = "Point"
        
        # Handle legacy format (weather_forecasts/air_quality_forecasts) - convert to days
        if "days" not in doc or not doc.get("days"):
            # Legacy format: convert flat arrays to days structure
            weather_points = []
            air_points = []
            
            if "weather_forecasts" in doc and isinstance(doc["weather_forecasts"], list):
                for item in doc["weather_forecasts"]:
                    if isinstance(item, dict):
                        if "timestamp" in item:
                            if isinstance(item["timestamp"], str):
                                item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                            elif isinstance(item["timestamp"], (int, float)):
                                item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                        weather_points.append(WeatherForecastPoint(**item))
            
            if "air_quality_forecasts" in doc and isinstance(doc["air_quality_forecasts"], list):
                for item in doc["air_quality_forecasts"]:
                    if isinstance(item, dict):
                        if "timestamp" in item:
                            if isinstance(item["timestamp"], str):
                                item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                            elif isinstance(item["timestamp"], (int, float)):
                                item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                        air_points.append(AirQualityForecastPoint(**item))
            
            # Convert to days structure
            if weather_points or air_points:
                doc["days"] = self._organize_by_days(weather_points, air_points)
                # Remove legacy fields
                doc.pop("weather_forecasts", None)
                doc.pop("air_quality_forecasts", None)
        
        # Normalize days structure if present
        if "days" in doc and isinstance(doc["days"], list):
            normalized_days = []
            for day_item in doc["days"]:
                if isinstance(day_item, dict):
                    # Normalize weather_forecasts in day
                    if "weather_forecasts" in day_item and isinstance(day_item["weather_forecasts"], list):
                        normalized_weather = []
                        for item in day_item["weather_forecasts"]:
                            if isinstance(item, dict):
                                if "timestamp" in item:
                                    if isinstance(item["timestamp"], str):
                                        item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                    elif isinstance(item["timestamp"], (int, float)):
                                        item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                                normalized_weather.append(item)
                            else:
                                normalized_weather.append(item)
                        day_item["weather_forecasts"] = normalized_weather
                    
                    # Normalize air_quality_forecasts in day
                    if "air_quality_forecasts" in day_item and isinstance(day_item["air_quality_forecasts"], list):
                        normalized_air = []
                        for item in day_item["air_quality_forecasts"]:
                            if isinstance(item, dict):
                                if "timestamp" in item:
                                    if isinstance(item["timestamp"], str):
                                        item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                    elif isinstance(item["timestamp"], (int, float)):
                                        item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                                normalized_air.append(item)
                            else:
                                normalized_air.append(item)
                        day_item["air_quality_forecasts"] = normalized_air
                    
                    normalized_days.append(day_item)
                else:
                    normalized_days.append(day_item)
            doc["days"] = normalized_days
        
        forecast = WeatherForecast(**doc)
        
        # Filter by days if needed
        if days < 5:
            cutoff_date = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
            forecast.days = [
                day for day in forecast.days
                if day.date <= cutoff_date
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
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
            
            # Normalize location if needed
            if "location" in doc and isinstance(doc["location"], dict):
                if "type" not in doc["location"]:
                    doc["location"]["type"] = "Point"
            
            # Handle legacy format - convert to days structure (same logic as get_forecast)
            if "days" not in doc or not doc.get("days"):
                weather_points = []
                air_points = []
                
                if "weather_forecasts" in doc and isinstance(doc["weather_forecasts"], list):
                    for item in doc["weather_forecasts"]:
                        if isinstance(item, dict):
                            if "timestamp" in item:
                                if isinstance(item["timestamp"], str):
                                    item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                elif isinstance(item["timestamp"], (int, float)):
                                    item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                            weather_points.append(WeatherForecastPoint(**item))
                
                if "air_quality_forecasts" in doc and isinstance(doc["air_quality_forecasts"], list):
                    for item in doc["air_quality_forecasts"]:
                        if isinstance(item, dict):
                            if "timestamp" in item:
                                if isinstance(item["timestamp"], str):
                                    item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                elif isinstance(item["timestamp"], (int, float)):
                                    item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                            air_points.append(AirQualityForecastPoint(**item))
                
                if weather_points or air_points:
                    doc["days"] = self._organize_by_days(weather_points, air_points)
                    doc.pop("weather_forecasts", None)
                    doc.pop("air_quality_forecasts", None)
            
            # Normalize days structure
            if "days" in doc and isinstance(doc["days"], list):
                normalized_days = []
                for day_item in doc["days"]:
                    if isinstance(day_item, dict):
                        if "weather_forecasts" in day_item and isinstance(day_item["weather_forecasts"], list):
                            normalized_weather = []
                            for item in day_item["weather_forecasts"]:
                                if isinstance(item, dict):
                                    if "timestamp" in item:
                                        if isinstance(item["timestamp"], str):
                                            item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                        elif isinstance(item["timestamp"], (int, float)):
                                            item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                                    normalized_weather.append(item)
                                else:
                                    normalized_weather.append(item)
                            day_item["weather_forecasts"] = normalized_weather
                        
                        if "air_quality_forecasts" in day_item and isinstance(day_item["air_quality_forecasts"], list):
                            normalized_air = []
                            for item in day_item["air_quality_forecasts"]:
                                if isinstance(item, dict):
                                    if "timestamp" in item:
                                        if isinstance(item["timestamp"], str):
                                            item["timestamp"] = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                                        elif isinstance(item["timestamp"], (int, float)):
                                            item["timestamp"] = datetime.fromtimestamp(item["timestamp"])
                                    normalized_air.append(item)
                                else:
                                    normalized_air.append(item)
                            day_item["air_quality_forecasts"] = normalized_air
                        
                        normalized_days.append(day_item)
                    else:
                        normalized_days.append(day_item)
                doc["days"] = normalized_days
            
            forecasts.append(WeatherForecast(**doc))
        
        return forecasts

