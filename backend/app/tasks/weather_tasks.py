# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Celery Scheduled Tasks for Weather Data Collection & Aggregation

Schedule:
- Real-time fetch: Every 1 minute (for fresh data)
- Hourly aggregation: Every 1 hour
- Daily aggregation: Every day at 00:05
- Monthly aggregation: Every month on 1st at 00:10
- Forecast fetch: Every 6 hours
"""

import logging
import asyncio
from datetime import datetime, timedelta
from celery import shared_task
from celery.schedules import crontab

from app.tasks import celery_app
from app.db.mongodb import database
from app.services.weather.weather_service import (
    WeatherService,
    collect_weather_data_for_location,
    collect_all_locations_data
)
from app.services.weather.weather_aggregation import (
    WeatherAggregationService,
    round_to_hour,
    round_to_day,
    round_to_month
)
from app.services.weather.forecast_service import ForecastService

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async function in sync context (Celery)"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@shared_task(name="weather.fetch_realtime_all_locations", bind=True)
def task_fetch_realtime_all_locations(self):
    """
    Fetch real-time weather data for all active locations
    Runs every 1 minute for fresh data
    
    Flow:
    1. Get all active locations
    2. For each location, fetch from OpenWeatherMap + OpenAQ
    3. Merge and save to weather_raw collection
    4. Data will be auto-deleted after 24h (TTL index)
    """
    try:
        logger.info("🔄 Starting real-time weather data fetch (all locations)")
        
        # Run async function
        run_async(collect_all_locations_data(database))
        
        logger.info("✅ Real-time weather data fetch completed")
        return {"status": "success", "message": "Real-time data collected for all locations"}
        
    except Exception as e:
        logger.error(f"❌ Error in real-time fetch task: {e}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(name="weather.aggregate_hourly_all_locations", bind=True)
def task_aggregate_hourly_all_locations(self):
    """
    Aggregate raw data into hourly summaries for all locations
    Runs every 1 hour
    
    Flow:
    1. Get all active locations
    2. For each location, aggregate last hour's raw data
    3. Save to weather_hourly collection
    4. Hourly data has TTL 7 days
    """
    try:
        logger.info("📊 Starting hourly aggregation (all locations)")
        
        service = WeatherAggregationService(database)
        
        # Aggregate last hour for all locations
        run_async(service.aggregate_all_hours(hours_back=1))
        
        logger.info("✅ Hourly aggregation completed")
        return {"status": "success", "message": "Hourly aggregation completed for all locations"}
        
    except Exception as e:
        logger.error(f"❌ Error in hourly aggregation task: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=300, max_retries=2)


@shared_task(name="weather.aggregate_daily_all_locations", bind=True)
def task_aggregate_daily_all_locations(self):
    """
    Aggregate hourly data into daily summaries for all locations
    Runs every day at 00:05
    
    Flow:
    1. Get all active locations
    2. For each location, aggregate yesterday's hourly data
    3. Save to weather_daily collection
    4. Daily data has TTL 30 days
    """
    try:
        logger.info("📊 Starting daily aggregation (all locations)")
        
        service = WeatherAggregationService(database)
        
        # Aggregate yesterday for all locations
        run_async(service.aggregate_all_days(days_back=1))
        
        logger.info("✅ Daily aggregation completed")
        return {"status": "success", "message": "Daily aggregation completed for all locations"}
        
    except Exception as e:
        logger.error(f"❌ Error in daily aggregation task: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=600, max_retries=2)


@shared_task(name="weather.aggregate_monthly_all_locations", bind=True)
def task_aggregate_monthly_all_locations(self):
    """
    Aggregate daily data into monthly summaries for all locations
    Runs every month on 1st at 00:10
    
    Flow:
    1. Get all active locations
    2. For each location, aggregate last month's daily data
    3. Save to weather_monthly collection
    4. Monthly data is permanent (no TTL) for long-term analysis
    """
    try:
        logger.info("📊 Starting monthly aggregation (all locations)")
        
        service = WeatherAggregationService(database)
        
        # Aggregate last month for all locations
        now = datetime.utcnow()
        last_month = now - timedelta(days=32)  # Go back to ensure we get last month
        year = last_month.year
        month = last_month.month
        
        locations = run_async(database["weather_locations"].find({"active": True}).to_list(None))
        
        for location in locations:
            location_id = location["location_id"]
            run_async(service.aggregate_monthly(location_id, year, month))
        
        logger.info("✅ Monthly aggregation completed")
        return {"status": "success", "message": f"Monthly aggregation completed for {year}-{month:02d}"}
        
    except Exception as e:
        logger.error(f"❌ Error in monthly aggregation task: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=1800, max_retries=2)


@shared_task(name="weather.fetch_forecast_all_locations", bind=True)
def task_fetch_forecast_all_locations(self):
    """
    Fetch 5-day weather forecast for all active locations
    Runs every 6 hours
    
    Flow:
    1. Get all active locations
    2. For each location, fetch forecast from OpenWeatherMap
    3. Save to weather_forecast collection (overwrites old forecast)
    4. Forecast is valid for 5 days
    """
    try:
        logger.info("🌤️  Starting forecast fetch (all locations)")
        
        weather_service = WeatherService(database)
        forecast_service = ForecastService(database)
        
        locations = run_async(weather_service.get_all_active_locations())
        
        success_count = 0
        for location in locations:
            try:
                success = run_async(
                    forecast_service.fetch_and_save_forecast(
                        location.location_id,
                        location.name,
                        location.location
                    )
                )
                if success:
                    success_count += 1
            except Exception as e:
                logger.warning(f"Failed to fetch forecast for {location.location_id}: {e}")
                continue
        
        logger.info(f"✅ Forecast fetch completed ({success_count}/{len(locations)} locations)")
        return {
            "status": "success",
            "message": f"Forecast fetched for {success_count}/{len(locations)} locations"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in forecast fetch task: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=1800, max_retries=2)


# Configure Celery Beat schedule
celery_app.conf.beat_schedule = {
    # Real-time fetch: Every 1 minute
    "fetch-realtime-weather": {
        "task": "weather.fetch_realtime_all_locations",
        "schedule": 60.0,  # 60 seconds = 1 minute
        "options": {"expires": 120}  # Task expires after 2 minutes if not picked up
    },
    
    # Hourly aggregation: Every 1 hour (at minute 0)
    "aggregate-hourly-weather": {
        "task": "weather.aggregate_hourly_all_locations",
        "schedule": crontab(minute=0),  # Every hour at :00
        "options": {"expires": 3600}
    },
    
    # Daily aggregation: Every day at 00:05
    "aggregate-daily-weather": {
        "task": "weather.aggregate_daily_all_locations",
        "schedule": crontab(hour=0, minute=5),  # 00:05 every day
        "options": {"expires": 86400}
    },
    
    # Monthly aggregation: Every month on 1st at 00:10
    "aggregate-monthly-weather": {
        "task": "weather.aggregate_monthly_all_locations",
        "schedule": crontab(day_of_month=1, hour=0, minute=10),  # 1st of month at 00:10
        "options": {"expires": 86400 * 2}
    },
    
    # Forecast fetch: Every 6 hours
    "fetch-forecast-weather": {
        "task": "weather.fetch_forecast_all_locations",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours at :00
        "options": {"expires": 21600}
    },
}

# Set timezone for schedule
celery_app.conf.timezone = "UTC"

