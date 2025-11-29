# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather Data Processing & Storage Service
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.weather import (
    WeatherRaw, WeatherData, AirQualityData, GeoLocation,
    WeatherHourly, WeatherDaily, WeatherMonthly, WeatherLocation
)
from app.services.weather_api import fetch_weather_data, fetch_openaq_data

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather data operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.weather_raw = db["weather_raw"]
        self.weather_hourly = db["weather_hourly"]
        self.weather_daily = db["weather_daily"]
        self.weather_monthly = db["weather_monthly"]
        self.weather_locations = db["weather_locations"]
    
    async def initialize_indexes(self):
        """Create necessary indexes"""
        try:
            # weather_raw indexes
            await self.weather_raw.create_index([("location", "2dsphere")])
            await self.weather_raw.create_index([("timestamp", 1), ("location_id", 1)])
            await self.weather_raw.create_index([("created_at", 1)], expireAfterSeconds=604800)  # 7 days TTL
            
            # weather_hourly indexes
            await self.weather_hourly.create_index([("location", "2dsphere")])
            await self.weather_hourly.create_index([("hour", 1), ("location_id", 1)], unique=True)
            await self.weather_hourly.create_index([("location_id", 1), ("hour", -1)])
            await self.weather_hourly.create_index([("created_at", 1)], expireAfterSeconds=7776000)  # 90 days TTL
            
            # weather_daily indexes
            await self.weather_daily.create_index([("location", "2dsphere")])
            await self.weather_daily.create_index([("date", 1), ("location_id", 1)], unique=True)
            await self.weather_daily.create_index([("location_id", 1), ("date", -1)])
            await self.weather_daily.create_index([("created_at", 1)], expireAfterSeconds=63072000)  # 2 years TTL
            
            # weather_monthly indexes
            await self.weather_monthly.create_index([("location", "2dsphere")])
            await self.weather_monthly.create_index([("year", 1), ("month", 1), ("location_id", 1)], unique=True)
            await self.weather_monthly.create_index([("location_id", 1), ("year", -1), ("month", -1)])
            
            # weather_locations indexes
            await self.weather_locations.create_index([("location_id", 1)], unique=True)
            await self.weather_locations.create_index([("location", "2dsphere")])
            await self.weather_locations.create_index([("external_ids.openweathermap_id", 1)])
            await self.weather_locations.create_index([("external_ids.openaq_location_id", 1)])
            
            logger.info("Weather database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    async def get_location(self, location_id: str) -> Optional[WeatherLocation]:
        """Get location by ID"""
        doc = await self.weather_locations.find_one({"location_id": location_id})
        if doc:
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            return WeatherLocation(**doc)
        return None
    
    async def get_all_active_locations(self) -> List[WeatherLocation]:
        """Get all active monitoring locations"""
        cursor = self.weather_locations.find({"active": True})
        locations = []
        async for doc in cursor:
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            locations.append(WeatherLocation(**doc))
        return locations
    
    def merge_air_quality_data(
        self,
        openweathermap_aq: Optional[Dict[str, Any]],
        openaq_aq: Optional[Dict[str, Any]],
        owm_location: tuple[float, float],
        openaq_location: Optional[tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Merge air quality data từ 2 sources với logic thông minh
        
        Logic:
        1. Cùng datetime + Cùng vị trí + Cùng parameter
           → Chỉ lấy OpenAQ (chính xác hơn)
        
        2. Khác datetime HOẶC Khác vị trí
           → Lưu cả 2 (vì là 2 measurements khác nhau)
        
        Thresholds:
        - Time diff: < 10 phút = cùng time
        - Distance: < 1km = cùng vị trí
        
        Args:
            openweathermap_aq: Air quality từ OpenWeatherMap
            openaq_aq: Air quality từ OpenAQ
            owm_location: (lat, lon) của OWM measurement
            openaq_location: (lat, lon) của OpenAQ measurement (nếu có)
        
        Returns:
            Merged air quality data
        """
        merged = {}
        
        if not openweathermap_aq and not openaq_aq:
            return merged
        
        if not openweathermap_aq:
            return {**openaq_aq.copy(), "_sources": ["openaq"]}
        
        if not openaq_aq:
            return {**openweathermap_aq.copy(), "_sources": ["openweathermap"]}
        
        # Check datetime difference
        owm_time = openweathermap_aq.get("timestamp")
        openaq_time = openaq_aq.get("timestamp")
        
        same_time = False
        if owm_time and openaq_time:
            time_diff = abs((owm_time - openaq_time).total_seconds())
            same_time = time_diff < 600  # < 10 phút
        
        # Check location distance
        same_location = False
        if openaq_location:
            distance = self._calculate_distance(owm_location, openaq_location)
            same_location = distance < 1000  # < 1km
        
        # Decision: Cùng time VÀ cùng vị trí?
        is_same_measurement = same_time and same_location
        
        if is_same_measurement:
            logger.info(
                f"Same time & location detected - "
                f"Using OpenAQ only (priority)"
            )
        
        # Parameters có thể có từ cả 2 sources
        common_params = ["pm2_5", "pm10", "co", "no2", "o3", "so2"]
        
        for param in common_params:
            owm_value = openweathermap_aq.get(param)
            oaq_value = openaq_aq.get(param)
            
            if oaq_value is not None and owm_value is not None:
                # Cả 2 đều có
                
                if is_same_measurement:
                    # ✅ Cùng time + cùng vị trí → Chỉ lấy OpenAQ
                    merged[param] = oaq_value
                else:
                    # ❗ Khác time HOẶC khác vị trí → Lưu cả 2
                    merged[param] = oaq_value  # Primary = OpenAQ
                    merged[f"{param}_openaq"] = {
                        "value": oaq_value,
                        "location": openaq_location if openaq_location else owm_location,
                        "timestamp": openaq_time
                    }
                    merged[f"{param}_owm"] = {
                        "value": owm_value,
                        "location": owm_location,
                        "timestamp": owm_time
                    }
                    
                    logger.info(
                        f"{param}: Different time/location - keeping both - "
                        f"OpenAQ={oaq_value}, OWM={owm_value}"
                    )
                    
            elif oaq_value is not None:
                # Chỉ OpenAQ có
                merged[param] = oaq_value
                
            elif owm_value is not None:
                # Chỉ OpenWeatherMap có
                merged[param] = owm_value
        
        # Parameters chỉ có ở OpenWeatherMap
        owm_only = ["no", "nh3"]
        for param in owm_only:
            if param in openweathermap_aq:
                merged[param] = openweathermap_aq[param]
        
        # AQI chỉ có từ OpenWeatherMap
        if "aqi" in openweathermap_aq:
            merged["aqi"] = openweathermap_aq["aqi"]
        
        # Metadata
        merged["_sources"] = []
        if openaq_aq:
            merged["_sources"].append("openaq")
        if openweathermap_aq:
            merged["_sources"].append("openweathermap")
        
        merged["_same_measurement"] = is_same_measurement
        
        return merged
    
    def _calculate_distance(
        self,
        loc1: tuple[float, float],
        loc2: tuple[float, float]
    ) -> float:
        """
        Tính khoảng cách giữa 2 tọa độ (Haversine formula)
        
        Args:
            loc1: (lat1, lon1)
            loc2: (lat2, lon2)
        
        Returns:
            Distance in meters
        """
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Earth radius in meters
        R = 6371000
        
        # Convert to radians
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        # Haversine formula
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance
    
    async def save_raw_data(
        self,
        location: WeatherLocation,
        weather_data: Optional[Dict[str, Any]],
        air_quality_data: Optional[Dict[str, Any]],
        source: str = "openweathermap"
    ) -> bool:
        """
        Save raw weather/air quality data
        
        Args:
            location: Location object
            weather_data: Parsed weather data
            air_quality_data: Parsed air quality data
            source: Data source
        
        Returns:
            True if data was saved (new or significantly different)
        """
        try:
            # Check if we should save (avoid duplicates and insignificant changes)
            should_save = await self._should_save_data(
                location.location_id,
                weather_data,
                air_quality_data
            )
            
            if not should_save:
                logger.debug(f"Skipping save for {location.location_id} - no significant changes")
                return False
            
            # Prepare document
            doc = WeatherRaw(
                location=location.location,
                location_name=location.name,
                location_id=location.location_id,
                timestamp=weather_data.get("timestamp") if weather_data else air_quality_data.get("timestamp"),
                weather=WeatherData(**weather_data) if weather_data else None,
                air_quality=AirQualityData(**air_quality_data) if air_quality_data else None,
                source=source
            )
            
            # Insert to database
            await self.weather_raw.insert_one(doc.model_dump(by_alias=True, exclude={"id"}))
            
            # Update location stats
            await self.weather_locations.update_one(
                {"location_id": location.location_id},
                {
                    "$set": {"stats.last_measurement": datetime.utcnow()},
                    "$inc": {"stats.total_measurements": 1}
                }
            )
            
            logger.info(f"Saved raw data for {location.location_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
            return False
    
    async def _should_save_data(
        self,
        location_id: str,
        weather_data: Optional[Dict[str, Any]],
        air_quality_data: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Determine if data should be saved based on changes
        
        Logic:
        - Always save if no recent data (>30 min)
        - Save if significant change in key metrics (>5%)
        - Save if AQI level changed
        - Save if weather condition changed
        """
        # Get last saved data
        last_doc = await self.weather_raw.find_one(
            {"location_id": location_id},
            sort=[("timestamp", -1)]
        )
        
        if not last_doc:
            return True  # No previous data, save
        
        # Check time since last save
        last_timestamp = last_doc.get("timestamp")
        if last_timestamp and (datetime.utcnow() - last_timestamp) > timedelta(minutes=30):
            return True  # More than 30 min, save
        
        # Check for significant changes
        if weather_data and last_doc.get("weather"):
            old_weather = last_doc["weather"]
            
            # Temperature change > 2°C
            if abs(weather_data.get("temp", 0) - old_weather.get("temp", 0)) > 2:
                return True
            
            # Condition changed
            if weather_data.get("condition") != old_weather.get("condition"):
                return True
            
            # Rain started/stopped
            if (weather_data.get("rain_1h", 0) > 0) != (old_weather.get("rain_1h", 0) > 0):
                return True
        
        if air_quality_data and last_doc.get("air_quality"):
            old_aq = last_doc["air_quality"]
            
            # AQI level changed
            if air_quality_data.get("aqi") != old_aq.get("aqi"):
                return True
            
            # PM2.5 change > 10%
            old_pm25 = old_aq.get("pm2_5", 0)
            new_pm25 = air_quality_data.get("pm2_5", 0)
            if old_pm25 > 0 and abs(new_pm25 - old_pm25) / old_pm25 > 0.1:
                return True
        
        return False  # No significant changes
    
    async def get_latest_data(self, location_id: str) -> Optional[WeatherRaw]:
        """Get latest raw data for a location"""
        doc = await self.weather_raw.find_one(
            {"location_id": location_id},
            sort=[("timestamp", -1)]
        )
        if doc:
            return WeatherRaw(**doc)
        return None
    
    async def get_hourly_data(
        self,
        location_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[WeatherHourly]:
        """Get hourly data for a time range"""
        cursor = self.weather_hourly.find(
            {
                "location_id": location_id,
                "hour": {"$gte": start_time, "$lte": end_time}
            }
        ).sort("hour", 1)
        
        data = []
        async for doc in cursor:
            data.append(WeatherHourly(**doc))
        return data
    
    async def get_daily_data(
        self,
        location_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherDaily]:
        """Get daily data for a date range"""
        cursor = self.weather_daily.find(
            {
                "location_id": location_id,
                "date": {"$gte": start_date, "$lte": end_date}
            }
        ).sort("date", 1)
        
        data = []
        async for doc in cursor:
            data.append(WeatherDaily(**doc))
        return data
    
    async def get_monthly_data(
        self,
        location_id: str,
        year: Optional[int] = None
    ) -> List[WeatherMonthly]:
        """Get monthly data for a year"""
        query = {"location_id": location_id}
        if year:
            query["year"] = year
        
        cursor = self.weather_monthly.find(query).sort([("year", -1), ("month", -1)])
        
        data = []
        async for doc in cursor:
            data.append(WeatherMonthly(**doc))
        return data
    
    async def find_nearby_locations(
        self,
        lon: float,
        lat: float,
        max_distance: int = 10000
    ) -> List[WeatherLocation]:
        """
        Find locations near a point
        
        Args:
            lon: Longitude
            lat: Latitude
            max_distance: Maximum distance in meters
        
        Returns:
            List of nearby locations
        """
        cursor = self.weather_locations.find(
            {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "$maxDistance": max_distance
                    }
                },
                "active": True
            }
        ).limit(10)
        
        locations = []
        async for doc in cursor:
            locations.append(WeatherLocation(**doc))
        return locations


async def collect_weather_data_for_location(
    db: AsyncIOMotorDatabase,
    location: WeatherLocation
) -> bool:
    """
    Collect weather data for a single location
    
    Flow:
    1. Fetch từ OpenWeatherMap (weather + air quality)
    2. Fetch từ OpenAQ (air quality)
    3. Merge air quality data với priority (OpenAQ > OpenWeatherMap)
    4. Save merged data
    
    Args:
        db: MongoDB database
        location: Location to collect data for
    
    Returns:
        True if data was collected successfully
    """
    service = WeatherService(db)
    
    try:
        lat = location.location.coordinates[1]
        lon = location.location.coordinates[0]
        
        weather_data = None
        owm_air_quality = None
        openaq_air_quality = None
        
        # 1. Fetch từ OpenWeatherMap
        if "openweathermap" in location.collection_config.sources:
            data = await fetch_weather_data(lat, lon)
            weather_data = data.get("weather")
            owm_air_quality = data.get("air_quality")
        
        # 2. Fetch từ OpenAQ
        if "openaq" in location.collection_config.sources:
            # Ưu tiên dùng location_id nếu có
            if location.external_ids.openaq_location_id:
                from app.services.weather_api import fetch_openaq_location_by_id
                openaq_result = await fetch_openaq_location_by_id(
                    location.external_ids.openaq_location_id
                )
                if openaq_result and openaq_result.get("measurements"):
                    openaq_air_quality = openaq_result["measurements"]
            else:
                # Fallback: tìm locations gần đó
                openaq_data = await fetch_openaq_data(
                    lat, lon,
                    radius=location.monitoring_radius
                )
                
                # Lấy trạm gần nhất
                if openaq_data and len(openaq_data) > 0:
                    closest = openaq_data[0]
                    openaq_air_quality = closest.get("measurements")
        
        # 3. Merge air quality data với location & time info
        owm_location = (lat, lon)
        openaq_location = None
        if openaq_result and openaq_result.get("latitude") and openaq_result.get("longitude"):
            openaq_location = (openaq_result["latitude"], openaq_result["longitude"])
        
        merged_air_quality = service.merge_air_quality_data(
            owm_air_quality,
            openaq_air_quality,
            owm_location,
            openaq_location
        )
        
        # 4. Save merged data
        if weather_data or merged_air_quality:
            await service.save_raw_data(
                location=location,
                weather_data=weather_data,
                air_quality_data=merged_air_quality,
                source="merged"  # Indicate this is merged from multiple sources
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Error collecting data for {location.location_id}: {e}")
        return False


async def collect_all_locations_data(db: AsyncIOMotorDatabase):
    """Collect data for all active locations"""
    service = WeatherService(db)
    locations = await service.get_all_active_locations()
    
    logger.info(f"Collecting data for {len(locations)} locations")
    
    for location in locations:
        if not location.collection_config.enabled:
            continue
        
        await collect_weather_data_for_location(db, location)
    
    logger.info("Data collection completed")


