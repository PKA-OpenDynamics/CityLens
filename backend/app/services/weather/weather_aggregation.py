# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather Data Aggregation Service
Aggregates raw data into hourly, daily, and monthly summaries
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.weather import (
    WeatherHourly, WeatherDaily, WeatherMonthly,
    WeatherHourlyStats, AirQualityHourlyStats,
    WeatherDailyStats, AirQualityDailyStats,
    WeatherMonthlyStats, AirQualityMonthlyStats,
    GeoLocation
)

logger = logging.getLogger(__name__)


def round_to_hour(dt: datetime) -> datetime:
    """Round datetime to the start of the hour"""
    return dt.replace(minute=0, second=0, microsecond=0)


def round_to_day(dt: datetime) -> datetime:
    """Round datetime to the start of the day"""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def round_to_month(dt: datetime) -> datetime:
    """Round datetime to the start of the month"""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class WeatherAggregationService:
    """Service for aggregating weather data"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.weather_raw = db["weather_raw"]
        self.weather_hourly = db["weather_hourly"]
        self.weather_daily = db["weather_daily"]
        self.weather_monthly = db["weather_monthly"]
        self.weather_locations = db["weather_locations"]
    
    async def aggregate_hourly(self, location_id: str, hour: datetime):
        """
        Aggregate raw data into hourly summary
        
        Args:
            location_id: Location identifier
            hour: Hour to aggregate (should be rounded to hour)
        """
        try:
            hour = round_to_hour(hour)
            next_hour = hour + timedelta(hours=1)
            
            # Get location info
            location_doc = await self.weather_locations.find_one({"location_id": location_id})
            if not location_doc:
                logger.error(f"Location not found: {location_id}")
                return
            
            # Fetch raw data for this hour
            cursor = self.weather_raw.find({
                "location_id": location_id,
                "timestamp": {"$gte": hour, "$lt": next_hour}
            }).sort("timestamp", 1)
            
            raw_data = []
            async for doc in cursor:
                raw_data.append(doc)
            
            if not raw_data:
                logger.debug(f"No raw data for {location_id} at {hour}")
                return
            
            # Aggregate weather data
            weather_stats = self._aggregate_weather_stats(raw_data)
            
            # Aggregate air quality data
            aq_stats = self._aggregate_air_quality_stats(raw_data)
            
            # Create or update hourly document
            hourly_doc = {
                "location_id": location_id,
                "location_name": location_doc["name"],
                "location": location_doc["location"],
                "hour": hour,
                "weather": weather_stats,
                "air_quality": aq_stats,
                "updated_at": datetime.utcnow()
            }
            
            # Upsert
            await self.weather_hourly.update_one(
                {"location_id": location_id, "hour": hour},
                {"$set": hourly_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )
            
            logger.info(f"Aggregated hourly data for {location_id} at {hour}")
            
        except Exception as e:
            logger.error(f"Error aggregating hourly data: {e}")
    
    def _aggregate_weather_stats(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate weather statistics from raw data"""
        temps = []
        humidity_vals = []
        pressure_vals = []
        wind_speeds = []
        wind_gusts = []
        rain_total = 0.0
        conditions = []
        
        for doc in raw_data:
            weather = doc.get("weather", {})
            if not weather:
                continue
            
            if weather.get("temp") is not None:
                temps.append(weather["temp"])
            if weather.get("humidity") is not None:
                humidity_vals.append(weather["humidity"])
            if weather.get("pressure") is not None:
                pressure_vals.append(weather["pressure"])
            if weather.get("wind_speed") is not None:
                wind_speeds.append(weather["wind_speed"])
            if weather.get("wind_gust") is not None:
                wind_gusts.append(weather["wind_gust"])
            if weather.get("rain_1h") is not None:
                rain_total += weather["rain_1h"]
            if weather.get("condition"):
                conditions.append(weather["condition"])
        
        # Calculate statistics
        stats = {
            "temp_avg": round(sum(temps) / len(temps), 1) if temps else None,
            "temp_min": round(min(temps), 1) if temps else None,
            "temp_max": round(max(temps), 1) if temps else None,
            "temp_samples": len(temps),
            
            "humidity_avg": round(sum(humidity_vals) / len(humidity_vals)) if humidity_vals else None,
            "humidity_min": min(humidity_vals) if humidity_vals else None,
            "humidity_max": max(humidity_vals) if humidity_vals else None,
            
            "pressure_avg": round(sum(pressure_vals) / len(pressure_vals)) if pressure_vals else None,
            "wind_speed_avg": round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None,
            "wind_speed_max": round(max(wind_speeds + wind_gusts), 1) if (wind_speeds or wind_gusts) else None,
            
            "rain_total": round(rain_total, 1),
            
            "condition_mode": Counter(conditions).most_common(1)[0][0] if conditions else None
        }
        
        return stats
    
    def _aggregate_air_quality_stats(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate air quality statistics from raw data"""
        aqis = []
        pm2_5_vals = []
        pm10_vals = []
        co_vals = []
        no2_vals = []
        o3_vals = []
        so2_vals = []
        
        for doc in raw_data:
            aq = doc.get("air_quality", {})
            if not aq:
                continue
            
            if aq.get("aqi") is not None:
                aqis.append(aq["aqi"])
            if aq.get("pm2_5") is not None:
                pm2_5_vals.append(aq["pm2_5"])
            if aq.get("pm10") is not None:
                pm10_vals.append(aq["pm10"])
            if aq.get("co") is not None:
                co_vals.append(aq["co"])
            if aq.get("no2") is not None:
                no2_vals.append(aq["no2"])
            if aq.get("o3") is not None:
                o3_vals.append(aq["o3"])
            if aq.get("so2") is not None:
                so2_vals.append(aq["so2"])
        
        stats = {
            "aqi_mode": Counter(aqis).most_common(1)[0][0] if aqis else None,
            "aqi_max": max(aqis) if aqis else None,
            
            "pm2_5_avg": round(sum(pm2_5_vals) / len(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_min": round(min(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_max": round(max(pm2_5_vals), 1) if pm2_5_vals else None,
            
            "pm10_avg": round(sum(pm10_vals) / len(pm10_vals), 1) if pm10_vals else None,
            "pm10_min": round(min(pm10_vals), 1) if pm10_vals else None,
            "pm10_max": round(max(pm10_vals), 1) if pm10_vals else None,
            
            "co_avg": round(sum(co_vals) / len(co_vals), 1) if co_vals else None,
            "no2_avg": round(sum(no2_vals) / len(no2_vals), 1) if no2_vals else None,
            "o3_avg": round(sum(o3_vals) / len(o3_vals), 1) if o3_vals else None,
            "so2_avg": round(sum(so2_vals) / len(so2_vals), 1) if so2_vals else None,
            
            "samples": len(aqis)
        }
        
        return stats
    
    async def aggregate_daily(self, location_id: str, date: datetime):
        """
        Aggregate hourly data into daily summary
        
        Args:
            location_id: Location identifier
            date: Date to aggregate (should be rounded to day)
        """
        try:
            date = round_to_day(date)
            next_day = date + timedelta(days=1)
            
            # Get location info
            location_doc = await self.weather_locations.find_one({"location_id": location_id})
            if not location_doc:
                logger.error(f"Location not found: {location_id}")
                return
            
            # Fetch hourly data for this day
            cursor = self.weather_hourly.find({
                "location_id": location_id,
                "hour": {"$gte": date, "$lt": next_day}
            }).sort("hour", 1)
            
            hourly_data = []
            async for doc in cursor:
                hourly_data.append(doc)
            
            if not hourly_data:
                logger.debug(f"No hourly data for {location_id} on {date}")
                return
            
            # Aggregate weather data
            weather_stats = self._aggregate_daily_weather_stats(hourly_data)
            
            # Aggregate air quality data
            aq_stats = self._aggregate_daily_air_quality_stats(hourly_data)
            
            # Create or update daily document
            daily_doc = {
                "location_id": location_id,
                "location_name": location_doc["name"],
                "location": location_doc["location"],
                "date": date,
                "weather": weather_stats,
                "air_quality": aq_stats,
                "updated_at": datetime.utcnow()
            }
            
            # Upsert
            await self.weather_daily.update_one(
                {"location_id": location_id, "date": date},
                {"$set": daily_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )
            
            logger.info(f"Aggregated daily data for {location_id} on {date.date()}")
            
        except Exception as e:
            logger.error(f"Error aggregating daily data: {e}")
    
    def _aggregate_daily_weather_stats(self, hourly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate daily weather statistics from hourly data"""
        temps = []
        humidity_vals = []
        pressure_vals = []
        wind_speeds = []
        rain_total = 0.0
        conditions_counter = Counter()
        
        for doc in hourly_data:
            weather = doc.get("weather", {})
            if not weather:
                continue
            
            if weather.get("temp_avg") is not None:
                temps.append(weather["temp_avg"])
            if weather.get("temp_min") is not None:
                temps.append(weather["temp_min"])
            if weather.get("temp_max") is not None:
                temps.append(weather["temp_max"])
            
            if weather.get("humidity_avg") is not None:
                humidity_vals.append(weather["humidity_avg"])
            if weather.get("pressure_avg") is not None:
                pressure_vals.append(weather["pressure_avg"])
            if weather.get("wind_speed_avg") is not None:
                wind_speeds.append(weather["wind_speed_avg"])
            if weather.get("wind_speed_max") is not None:
                wind_speeds.append(weather["wind_speed_max"])
            
            if weather.get("rain_total"):
                rain_total += weather["rain_total"]
            
            if weather.get("condition_mode"):
                conditions_counter[weather["condition_mode"]] += 1
        
        stats = {
            "temp_avg": round(sum(temps) / len(temps), 1) if temps else None,
            "temp_min": round(min(temps), 1) if temps else None,
            "temp_max": round(max(temps), 1) if temps else None,
            
            "humidity_avg": round(sum(humidity_vals) / len(humidity_vals)) if humidity_vals else None,
            "humidity_min": min(humidity_vals) if humidity_vals else None,
            "humidity_max": max(humidity_vals) if humidity_vals else None,
            
            "pressure_avg": round(sum(pressure_vals) / len(pressure_vals)) if pressure_vals else None,
            "wind_speed_avg": round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None,
            "wind_speed_max": round(max(wind_speeds), 1) if wind_speeds else None,
            
            "rain_total": round(rain_total, 1),
            
            "conditions": dict(conditions_counter),
            
            "samples": len(hourly_data)
        }
        
        return stats
    
    def _aggregate_daily_air_quality_stats(self, hourly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate daily air quality statistics from hourly data"""
        aqi_counter = Counter()
        pm2_5_vals = []
        pm10_vals = []
        co_vals = []
        no2_vals = []
        o3_vals = []
        so2_vals = []
        
        best_pm25 = float('inf')
        worst_pm25 = 0
        best_hour = None
        worst_hour = None
        
        for doc in hourly_data:
            aq = doc.get("air_quality", {})
            if not aq:
                continue
            
            if aq.get("aqi_mode") is not None:
                aqi_counter[str(aq["aqi_mode"])] += 1
            
            if aq.get("pm2_5_avg") is not None:
                pm2_5 = aq["pm2_5_avg"]
                pm2_5_vals.append(pm2_5)
                
                if pm2_5 < best_pm25:
                    best_pm25 = pm2_5
                    best_hour = doc.get("hour")
                if pm2_5 > worst_pm25:
                    worst_pm25 = pm2_5
                    worst_hour = doc.get("hour")
            
            if aq.get("pm10_avg") is not None:
                pm10_vals.append(aq["pm10_avg"])
            if aq.get("co_avg") is not None:
                co_vals.append(aq["co_avg"])
            if aq.get("no2_avg") is not None:
                no2_vals.append(aq["no2_avg"])
            if aq.get("o3_avg") is not None:
                o3_vals.append(aq["o3_avg"])
            if aq.get("so2_avg") is not None:
                so2_vals.append(aq["so2_avg"])
        
        stats = {
            "aqi_distribution": dict(aqi_counter),
            
            "pm2_5_avg": round(sum(pm2_5_vals) / len(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_min": round(min(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_max": round(max(pm2_5_vals), 1) if pm2_5_vals else None,
            
            "pm10_avg": round(sum(pm10_vals) / len(pm10_vals), 1) if pm10_vals else None,
            "pm10_min": round(min(pm10_vals), 1) if pm10_vals else None,
            "pm10_max": round(max(pm10_vals), 1) if pm10_vals else None,
            
            "co_avg": round(sum(co_vals) / len(co_vals), 1) if co_vals else None,
            "no2_avg": round(sum(no2_vals) / len(no2_vals), 1) if no2_vals else None,
            "o3_avg": round(sum(o3_vals) / len(o3_vals), 1) if o3_vals else None,
            "so2_avg": round(sum(so2_vals) / len(so2_vals), 1) if so2_vals else None,
            
            "best_hour": best_hour,
            "worst_hour": worst_hour,
            
            "samples": len(hourly_data)
        }
        
        return stats
    
    async def aggregate_monthly(self, location_id: str, year: int, month: int):
        """
        Aggregate daily data into monthly summary
        
        Args:
            location_id: Location identifier
            year: Year
            month: Month (1-12)
        """
        try:
            month_start = datetime(year, month, 1)
            if month == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month + 1, 1)
            
            # Get location info
            location_doc = await self.weather_locations.find_one({"location_id": location_id})
            if not location_doc:
                logger.error(f"Location not found: {location_id}")
                return
            
            # Fetch daily data for this month
            cursor = self.weather_daily.find({
                "location_id": location_id,
                "date": {"$gte": month_start, "$lt": next_month}
            }).sort("date", 1)
            
            daily_data = []
            async for doc in cursor:
                daily_data.append(doc)
            
            if not daily_data:
                logger.debug(f"No daily data for {location_id} in {year}-{month:02d}")
                return
            
            # Aggregate weather data
            weather_stats = self._aggregate_monthly_weather_stats(daily_data)
            
            # Aggregate air quality data
            aq_stats = self._aggregate_monthly_air_quality_stats(daily_data)
            
            # Create or update monthly document
            monthly_doc = {
                "location_id": location_id,
                "location_name": location_doc["name"],
                "location": location_doc["location"],
                "year": year,
                "month": month,
                "month_start": month_start,
                "weather": weather_stats,
                "air_quality": aq_stats,
                "updated_at": datetime.utcnow()
            }
            
            # Upsert
            await self.weather_monthly.update_one(
                {"location_id": location_id, "year": year, "month": month},
                {"$set": monthly_doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )
            
            logger.info(f"Aggregated monthly data for {location_id} in {year}-{month:02d}")
            
        except Exception as e:
            logger.error(f"Error aggregating monthly data: {e}")
    
    def _aggregate_monthly_weather_stats(self, daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate monthly weather statistics from daily data"""
        temps = []
        humidity_vals = []
        pressure_vals = []
        wind_speeds = []
        rain_total = 0.0
        rainy_days = 0
        conditions_counter = Counter()
        
        for doc in daily_data:
            weather = doc.get("weather", {})
            if not weather:
                continue
            
            if weather.get("temp_avg") is not None:
                temps.append(weather["temp_avg"])
            if weather.get("temp_min") is not None:
                temps.append(weather["temp_min"])
            if weather.get("temp_max") is not None:
                temps.append(weather["temp_max"])
            
            if weather.get("humidity_avg") is not None:
                humidity_vals.append(weather["humidity_avg"])
            if weather.get("pressure_avg") is not None:
                pressure_vals.append(weather["pressure_avg"])
            if weather.get("wind_speed_avg") is not None:
                wind_speeds.append(weather["wind_speed_avg"])
            
            if weather.get("rain_total"):
                rain_total += weather["rain_total"]
                if weather["rain_total"] > 1.0:  # Rainy day threshold
                    rainy_days += 1
            
            conditions = weather.get("conditions", {})
            for condition, count in conditions.items():
                conditions_counter[condition] += count
        
        stats = {
            "temp_avg": round(sum(temps) / len(temps), 1) if temps else None,
            "temp_min": round(min(temps), 1) if temps else None,
            "temp_max": round(max(temps), 1) if temps else None,
            
            "humidity_avg": round(sum(humidity_vals) / len(humidity_vals)) if humidity_vals else None,
            "pressure_avg": round(sum(pressure_vals) / len(pressure_vals)) if pressure_vals else None,
            "wind_speed_avg": round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else None,
            
            "rain_total": round(rain_total, 1),
            "rainy_days": rainy_days,
            
            "conditions": dict(conditions_counter),
            
            "days_with_data": len(daily_data)
        }
        
        return stats
    
    def _aggregate_monthly_air_quality_stats(self, daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate monthly air quality statistics from daily data"""
        aqi_counter = Counter()
        pm2_5_vals = []
        pm10_vals = []
        co_vals = []
        no2_vals = []
        o3_vals = []
        so2_vals = []
        
        best_pm25 = float('inf')
        worst_pm25 = 0
        best_day = None
        worst_day = None
        
        for doc in daily_data:
            aq = doc.get("air_quality", {})
            if not aq:
                continue
            
            aqi_dist = aq.get("aqi_distribution", {})
            for level, count in aqi_dist.items():
                aqi_counter[level] += count
            
            if aq.get("pm2_5_avg") is not None:
                pm2_5 = aq["pm2_5_avg"]
                pm2_5_vals.append(pm2_5)
                
                if pm2_5 < best_pm25:
                    best_pm25 = pm2_5
                    best_day = doc.get("date")
                if pm2_5 > worst_pm25:
                    worst_pm25 = pm2_5
                    worst_day = doc.get("date")
            
            if aq.get("pm2_5_min") is not None:
                pm2_5_vals.append(aq["pm2_5_min"])
            if aq.get("pm2_5_max") is not None:
                pm2_5_vals.append(aq["pm2_5_max"])
            
            if aq.get("pm10_avg") is not None:
                pm10_vals.append(aq["pm10_avg"])
            if aq.get("co_avg") is not None:
                co_vals.append(aq["co_avg"])
            if aq.get("no2_avg") is not None:
                no2_vals.append(aq["no2_avg"])
            if aq.get("o3_avg") is not None:
                o3_vals.append(aq["o3_avg"])
            if aq.get("so2_avg") is not None:
                so2_vals.append(aq["so2_avg"])
        
        stats = {
            "aqi_distribution": dict(aqi_counter),
            
            "pm2_5_avg": round(sum(pm2_5_vals) / len(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_min": round(min(pm2_5_vals), 1) if pm2_5_vals else None,
            "pm2_5_max": round(max(pm2_5_vals), 1) if pm2_5_vals else None,
            
            "pm10_avg": round(sum(pm10_vals) / len(pm10_vals), 1) if pm10_vals else None,
            "co_avg": round(sum(co_vals) / len(co_vals), 1) if co_vals else None,
            "no2_avg": round(sum(no2_vals) / len(no2_vals), 1) if no2_vals else None,
            "o3_avg": round(sum(o3_vals) / len(o3_vals), 1) if o3_vals else None,
            "so2_avg": round(sum(so2_vals) / len(so2_vals), 1) if so2_vals else None,
            
            "best_day": best_day,
            "worst_day": worst_day,
            
            "days_with_data": len(daily_data)
        }
        
        return stats
    
    async def aggregate_all_hours(self, hours_back: int = 24):
        """Aggregate last N hours for all locations"""
        locations = await self.weather_locations.find({"active": True}).to_list(None)
        
        for location in locations:
            location_id = location["location_id"]
            
            # Aggregate each hour
            now = datetime.utcnow()
            for i in range(hours_back):
                hour = round_to_hour(now - timedelta(hours=i))
                await self.aggregate_hourly(location_id, hour)
    
    async def aggregate_all_days(self, days_back: int = 7):
        """Aggregate last N days for all locations"""
        locations = await self.weather_locations.find({"active": True}).to_list(None)
        
        for location in locations:
            location_id = location["location_id"]
            
            # Aggregate each day
            now = datetime.utcnow()
            for i in range(days_back):
                date = round_to_day(now - timedelta(days=i))
                await self.aggregate_daily(location_id, date)
    
    async def aggregate_current_month(self):
        """Aggregate current month for all locations"""
        locations = await self.weather_locations.find({"active": True}).to_list(None)
        
        now = datetime.utcnow()
        year = now.year
        month = now.month
        
        for location in locations:
            location_id = location["location_id"]
            await self.aggregate_monthly(location_id, year, month)


