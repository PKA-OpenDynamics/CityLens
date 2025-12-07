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
from app.services.weather.weather_api import fetch_weather_data, fetch_openaq_data

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
            await self.weather_raw.create_index([("created_at", 1)], expireAfterSeconds=86400)  # 24 hours TTL
            
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
            from app.utils.weather_helpers import normalize_location_doc
            normalized_doc = normalize_location_doc(doc)
            return WeatherLocation(**normalized_doc)
        return None
    
    async def get_all_active_locations(self) -> List[WeatherLocation]:
        """Get all active monitoring locations"""
        cursor = self.weather_locations.find({"active": True})
        locations = []
        from app.utils.weather_helpers import normalize_location_doc
        
        async for doc in cursor:
            normalized_doc = normalize_location_doc(doc)
            locations.append(WeatherLocation(**normalized_doc))
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
        source: str = "openweathermap",
        skip_check: bool = False
    ) -> bool:
        """
        Save raw weather/air quality data
        
        Args:
            location: Location object
            weather_data: Parsed weather data
            air_quality_data: Parsed air quality data
            source: Data source
            skip_check: Skip should_save check for faster batch operations
        
        Returns:
            True if data was saved (new or significantly different)
        """
        try:
            # Check if we should save (avoid duplicates and insignificant changes)
            if not skip_check:
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
            
            # Update location stats (fire and forget for speed)
            try:
                await self.weather_locations.update_one(
                    {"location_id": location.location_id},
                    {
                        "$set": {"stats.last_measurement": datetime.utcnow()},
                        "$inc": {"stats.total_measurements": 1}
                    }
                )
            except Exception as e:
                logger.warning(f"Error updating stats for {location.location_id}: {e}")
            
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
        if last_timestamp and isinstance(last_timestamp, datetime):
            if (datetime.utcnow() - last_timestamp) > timedelta(minutes=30):
                return True  # More than 30 min, save
        
        # Check for significant changes
        if weather_data and last_doc.get("weather"):
            old_weather = last_doc["weather"]
            
            # Temperature change > 2°C
            old_temp = old_weather.get("temp")
            new_temp = weather_data.get("temp")
            if old_temp is not None and new_temp is not None:
                if abs(new_temp - old_temp) > 2:
                    return True
            
            # Condition changed
            if weather_data.get("condition") != old_weather.get("condition"):
                return True
            
            # Rain started/stopped
            old_rain = old_weather.get("rain_1h", 0) or 0
            new_rain = weather_data.get("rain_1h", 0) or 0
            if (new_rain > 0) != (old_rain > 0):
                return True
        
        if air_quality_data and last_doc.get("air_quality"):
            old_aq = last_doc["air_quality"]
            
            # AQI level changed
            old_aqi = old_aq.get("aqi")
            new_aqi = air_quality_data.get("aqi")
            if old_aqi is not None and new_aqi is not None and old_aqi != new_aqi:
                return True
            
            # PM2.5 change > 10%
            old_pm25 = old_aq.get("pm2_5")
            new_pm25 = air_quality_data.get("pm2_5")
            if old_pm25 is not None and new_pm25 is not None and old_pm25 > 0:
                if abs(new_pm25 - old_pm25) / old_pm25 > 0.1:
                    return True
        
        return False  # No significant changes
    
    async def get_latest_data(self, location_id: str) -> Optional[WeatherRaw]:
        """Get latest raw data for a location"""
        doc = await self.weather_raw.find_one(
            {"location_id": location_id},
            sort=[("timestamp", -1)]
        )
        if doc:
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
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
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
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
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
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
            # Convert _id to string if present
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
            
            # Normalize month field - convert datetime to int if needed
            if "month" in doc and isinstance(doc["month"], datetime):
                month_dt = doc["month"]
                doc["month"] = month_dt.month
                # Create month_start if missing
                if "month_start" not in doc:
                    from datetime import datetime as dt
                    doc["month_start"] = dt(month_dt.year, month_dt.month, 1, 0, 0, 0)
            
            # Ensure month_start exists
            if "month_start" not in doc and "month" in doc and "year" in doc:
                from datetime import datetime as dt
                doc["month_start"] = dt(doc["year"], doc["month"], 1, 0, 0, 0)
            
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
        from app.utils.weather_helpers import normalize_location_doc
        
        async for doc in cursor:
            normalized_doc = normalize_location_doc(doc)
            locations.append(WeatherLocation(**normalized_doc))
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
        openaq_result = None
        if "openaq" in location.collection_config.sources:
            # Ưu tiên dùng location_id nếu có
            if location.external_ids and location.external_ids.openaq_location_id:
                from app.services.weather.weather_api import fetch_openaq_location_by_id
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
                    # Store result for location extraction
                    openaq_result = closest
        
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
        
        # 4. Save data - save separately by source if we have data from multiple sources
        saved = False
        
        # Save OpenWeatherMap data (weather + air quality from OWM)
        # Skip should_save check for real-time data (TTL will handle cleanup)
        if weather_data or owm_air_quality:
            await service.save_raw_data(
                location=location,
                weather_data=weather_data,
                air_quality_data=owm_air_quality,
                source="openweathermap",
                skip_check=True  # Skip duplicate check for speed
            )
            saved = True
        
        # Save OpenAQ data separately if we have it and it's different from OWM
        if openaq_air_quality and openaq_air_quality != owm_air_quality:
            await service.save_raw_data(
                location=location,
                weather_data=None,
                air_quality_data=openaq_air_quality,
                source="openaq",
                skip_check=True  # Skip duplicate check for speed
            )
            saved = True
        
        # If we only have merged air quality (no separate sources), save with primary source
        if not saved and merged_air_quality:
            # Determine primary source
            primary_source = "openweathermap" if owm_air_quality else "openaq"
            await service.save_raw_data(
                location=location,
                weather_data=weather_data,
                air_quality_data=merged_air_quality,
                source=primary_source,
                skip_check=True  # Skip duplicate check for speed
            )
            saved = True
        
        return saved
        
    except Exception as e:
        logger.error(f"Error collecting data for {location.location_id}: {e}")
        return False


async def collect_all_locations_data(db: AsyncIOMotorDatabase):
    """Collect data for all active locations (parallel with batch writes)"""
    import asyncio
    from datetime import datetime
    
    service = WeatherService(db)
    locations = await service.get_all_active_locations()
    
    # Filter enabled locations
    enabled_locations = [loc for loc in locations if loc.collection_config.enabled]
    
    logger.info(f"Collecting data for {len(enabled_locations)} locations (parallel)")
    start_time = datetime.utcnow()
    
    # Fetch data for all locations in parallel
    tasks = [
        collect_weather_data_for_location(db, location)
        for location in enabled_locations
    ]
    
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Log any errors
    success_count = sum(1 for r in results if r is True)
    error_count = sum(1 for r in results if isinstance(r, Exception))
    
    elapsed = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Data collection completed: {success_count} succeeded, {error_count} errors in {elapsed:.2f}s")


