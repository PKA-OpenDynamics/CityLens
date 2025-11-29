# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather & Air Quality Data Models
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId


class GeoLocation(BaseModel):
    """GeoJSON Point"""
    type: str = "Point"
    coordinates: List[float] = Field(..., description="[longitude, latitude]")
    
    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError("Coordinates must be [longitude, latitude]")
        lon, lat = v
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v


class WeatherData(BaseModel):
    """Weather metrics"""
    temp: Optional[float] = Field(None, description="Temperature (°C)")
    feels_like: Optional[float] = Field(None, description="Feels like (°C)")
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    pressure: Optional[int] = Field(None, description="Atmospheric pressure (hPa)")
    humidity: Optional[int] = Field(None, description="Humidity (%)")
    visibility: Optional[int] = Field(None, description="Visibility (meters)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")
    wind_deg: Optional[int] = Field(None, description="Wind direction (degrees)")
    wind_gust: Optional[float] = Field(None, description="Wind gust (m/s)")
    clouds: Optional[int] = Field(None, description="Cloudiness (%)")
    rain_1h: Optional[float] = Field(None, description="Rain volume last 1h (mm)")
    rain_3h: Optional[float] = Field(None, description="Rain volume last 3h (mm)")
    condition: Optional[str] = Field(None, description="Weather condition")


class AirQualityData(BaseModel):
    """Air quality metrics"""
    aqi: Optional[int] = Field(None, description="Air Quality Index (1-5)")
    co: Optional[float] = Field(None, description="Carbon monoxide (μg/m³)")
    no: Optional[float] = Field(None, description="Nitrogen monoxide (μg/m³)")
    no2: Optional[float] = Field(None, description="Nitrogen dioxide (μg/m³)")
    o3: Optional[float] = Field(None, description="Ozone (μg/m³)")
    so2: Optional[float] = Field(None, description="Sulphur dioxide (μg/m³)")
    pm2_5: Optional[float] = Field(None, description="PM2.5 (μg/m³)")
    pm10: Optional[float] = Field(None, description="PM10 (μg/m³)")
    nh3: Optional[float] = Field(None, description="Ammonia (μg/m³)")


# === Raw Data Collection ===

class WeatherRaw(BaseModel):
    """Raw weather & air quality data (7-day retention)"""
    id: Optional[str] = Field(alias="_id", default=None)
    location: GeoLocation
    location_name: str
    location_id: str = Field(..., description="Standard location identifier")
    
    timestamp: datetime = Field(..., description="Measurement timestamp")
    
    weather: Optional[WeatherData] = None
    air_quality: Optional[AirQualityData] = None
    
    source: Literal["openweathermap", "openaq"] = Field(..., description="Data source")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Hourly Aggregated Data ===

class WeatherHourlyStats(BaseModel):
    """Hourly weather statistics"""
    temp_avg: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    temp_samples: int = 0
    
    humidity_avg: Optional[int] = None
    humidity_min: Optional[int] = None
    humidity_max: Optional[int] = None
    
    pressure_avg: Optional[int] = None
    wind_speed_avg: Optional[float] = None
    wind_speed_max: Optional[float] = None
    
    rain_total: float = 0.0
    
    condition_mode: Optional[str] = None


class AirQualityHourlyStats(BaseModel):
    """Hourly air quality statistics"""
    aqi_mode: Optional[int] = None
    aqi_max: Optional[int] = None
    
    pm2_5_avg: Optional[float] = None
    pm2_5_min: Optional[float] = None
    pm2_5_max: Optional[float] = None
    
    pm10_avg: Optional[float] = None
    pm10_min: Optional[float] = None
    pm10_max: Optional[float] = None
    
    co_avg: Optional[float] = None
    no2_avg: Optional[float] = None
    o3_avg: Optional[float] = None
    so2_avg: Optional[float] = None
    
    samples: int = 0


class WeatherHourly(BaseModel):
    """Hourly aggregated weather data (90-day retention)"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_name: str
    location: GeoLocation
    
    hour: datetime = Field(..., description="Hour timestamp (rounded)")
    
    weather: WeatherHourlyStats
    air_quality: AirQualityHourlyStats
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Daily Aggregated Data ===

class WeatherDailyStats(BaseModel):
    """Daily weather statistics"""
    temp_avg: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    
    humidity_avg: Optional[int] = None
    humidity_min: Optional[int] = None
    humidity_max: Optional[int] = None
    
    pressure_avg: Optional[int] = None
    wind_speed_avg: Optional[float] = None
    wind_speed_max: Optional[float] = None
    
    rain_total: float = 0.0
    
    conditions: Dict[str, int] = Field(default_factory=dict, description="Weather condition distribution")
    
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    
    samples: int = 0


class AirQualityDailyStats(BaseModel):
    """Daily air quality statistics"""
    aqi_distribution: Dict[str, int] = Field(default_factory=dict, description="AQI level distribution")
    
    pm2_5_avg: Optional[float] = None
    pm2_5_min: Optional[float] = None
    pm2_5_max: Optional[float] = None
    
    pm10_avg: Optional[float] = None
    pm10_min: Optional[float] = None
    pm10_max: Optional[float] = None
    
    co_avg: Optional[float] = None
    no2_avg: Optional[float] = None
    o3_avg: Optional[float] = None
    so2_avg: Optional[float] = None
    
    best_hour: Optional[datetime] = None
    worst_hour: Optional[datetime] = None
    
    samples: int = 0


class WeatherDaily(BaseModel):
    """Daily aggregated weather data (2-year retention)"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_name: str
    location: GeoLocation
    
    date: datetime = Field(..., description="Date at 00:00:00 UTC")
    
    weather: WeatherDailyStats
    air_quality: AirQualityDailyStats
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Weekly Aggregated Data ===

class WeatherWeeklyStats(BaseModel):
    """Weekly weather statistics"""
    temp_avg: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    
    humidity_avg: Optional[int] = None
    pressure_avg: Optional[int] = None
    wind_speed_avg: Optional[float] = None
    
    rain_total: float = 0.0
    rainy_days: int = 0
    
    conditions: Dict[str, int] = Field(default_factory=dict)
    
    days_with_data: int = 0


class AirQualityWeeklyStats(BaseModel):
    """Weekly air quality statistics"""
    aqi_distribution: Dict[str, int] = Field(default_factory=dict)
    
    pm2_5_avg: Optional[float] = None
    pm2_5_min: Optional[float] = None
    pm2_5_max: Optional[float] = None
    
    pm10_avg: Optional[float] = None
    co_avg: Optional[float] = None
    no2_avg: Optional[float] = None
    o3_avg: Optional[float] = None
    so2_avg: Optional[float] = None
    
    best_day: Optional[datetime] = None
    worst_day: Optional[datetime] = None
    
    days_with_data: int = 0


class WeatherWeekly(BaseModel):
    """Weekly aggregated weather data (6-month retention)"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_name: str
    location: GeoLocation
    
    year: int
    week: int = Field(..., description="ISO week number (1-53)")
    week_start: datetime = Field(..., description="Monday 00:00:00 UTC")
    week_end: datetime = Field(..., description="Sunday 23:59:59 UTC")
    
    weather: WeatherWeeklyStats
    air_quality: AirQualityWeeklyStats
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Monthly Aggregated Data ===

class WeatherMonthlyStats(BaseModel):
    """Monthly weather statistics"""
    temp_avg: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    
    humidity_avg: Optional[int] = None
    pressure_avg: Optional[int] = None
    wind_speed_avg: Optional[float] = None
    
    rain_total: float = 0.0
    rainy_days: int = 0
    
    conditions: Dict[str, int] = Field(default_factory=dict)
    
    days_with_data: int = 0


class AirQualityMonthlyStats(BaseModel):
    """Monthly air quality statistics"""
    aqi_distribution: Dict[str, int] = Field(default_factory=dict)
    
    pm2_5_avg: Optional[float] = None
    pm2_5_min: Optional[float] = None
    pm2_5_max: Optional[float] = None
    
    pm10_avg: Optional[float] = None
    co_avg: Optional[float] = None
    no2_avg: Optional[float] = None
    o3_avg: Optional[float] = None
    so2_avg: Optional[float] = None
    
    best_day: Optional[datetime] = None
    worst_day: Optional[datetime] = None
    
    days_with_data: int = 0


class WeatherMonthly(BaseModel):
    """Monthly aggregated weather data (permanent)"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_name: str
    location: GeoLocation
    
    year: int
    month: int
    month_start: datetime
    
    weather: WeatherMonthlyStats
    air_quality: AirQualityMonthlyStats
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Location Metadata ===

class LocationAddress(BaseModel):
    """Address information"""
    city: str
    district: Optional[str] = None
    country: str
    country_code: str


class LocationExternalIds(BaseModel):
    """External API identifiers"""
    openweathermap_id: Optional[int] = None
    openaq_location_id: Optional[int] = None


class LocationCollectionConfig(BaseModel):
    """Data collection configuration"""
    enabled: bool = True
    interval_minutes: int = 10
    sources: List[Literal["openweathermap", "openaq"]] = ["openweathermap"]


class LocationStats(BaseModel):
    """Location statistics"""
    first_measurement: Optional[datetime] = None
    last_measurement: Optional[datetime] = None
    total_measurements: int = 0


class WeatherLocation(BaseModel):
    """Monitoring location metadata"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str = Field(..., description="Unique location identifier")
    
    name: str
    name_vi: Optional[str] = None
    
    location: GeoLocation
    address: LocationAddress
    
    external_ids: LocationExternalIds
    
    type: Literal["urban", "suburban", "rural", "industrial"] = "urban"
    monitoring_radius: int = 5000  # meters
    
    collection_config: LocationCollectionConfig
    
    stats: LocationStats = Field(default_factory=LocationStats)
    
    lod_uri: Optional[str] = None
    
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


# === Forecast Data ===

class WeatherForecastPoint(BaseModel):
    """Single forecast point (3-hour interval)"""
    timestamp: datetime
    temp: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    wind_speed: Optional[float] = None
    wind_deg: Optional[int] = None
    clouds: Optional[int] = None
    rain_3h: Optional[float] = None
    condition: Optional[str] = None
    visibility: Optional[int] = None


class AirQualityForecastPoint(BaseModel):
    """Single air quality forecast point"""
    timestamp: datetime
    aqi: Optional[int] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None


class WeatherForecast(BaseModel):
    """5-day weather and air quality forecast for a location"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_name: str
    location: GeoLocation
    
    # Forecast points (3-hour intervals, up to 5 days = ~40 points)
    weather_forecasts: List[WeatherForecastPoint] = Field(default_factory=list)
    air_quality_forecasts: List[AirQualityForecastPoint] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(..., description="Forecast validity end time")
    
    class Config:
        populate_by_name = True


# === Real-time Response Models ===

class RealtimeWeatherResponse(BaseModel):
    """Optimized real-time weather response for mobile/web"""
    location_id: str
    location_name: str
    timestamp: datetime
    
    weather: Optional[WeatherData] = None
    air_quality: Optional[AirQualityData] = None
    
    # Status indicators
    data_age_seconds: Optional[int] = Field(None, description="Age of data in seconds")
    is_fresh: bool = Field(True, description="Whether data is fresh (< 10 minutes)")
    sources: List[str] = Field(default_factory=list, description="Data sources used")


class RealtimeWeatherSummaryResponse(BaseModel):
    """Summary of real-time data for multiple locations"""
    locations: List[RealtimeWeatherResponse]
    generated_at: datetime
    total_locations: int


