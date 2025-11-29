# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Weather API Clients (OpenWeatherMap & OpenAQ)
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenWeatherMapClient:
    """Client for OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not configured")
    
    async def get_current_weather(
        self,
        lat: float,
        lon: float,
        units: str = "metric"
    ) -> Optional[Dict[str, Any]]:
        """
        Get current weather data
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Units (metric, imperial, standard)
        
        Returns:
            Weather data dict or None if error
        """
        if not self.api_key:
            logger.error("OpenWeatherMap API key not available")
            return None
        
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting weather: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return None
    
    async def get_air_pollution(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict[str, Any]]:
        """
        Get current air pollution data
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Air pollution data dict or None if error
        """
        if not self.api_key:
            logger.error("OpenWeatherMap API key not available")
            return None
        
        try:
            url = f"{self.BASE_URL}/air_pollution"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting air pollution: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting air pollution: {e}")
            return None
    
    def parse_weather_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OpenWeatherMap weather response to our format
        
        Args:
            data: Raw API response
        
        Returns:
            Parsed weather data
        """
        try:
            main = data.get("main", {})
            wind = data.get("wind", {})
            clouds = data.get("clouds", {})
            rain = data.get("rain", {})
            weather = data.get("weather", [{}])[0]
            sys = data.get("sys", {})
            
            parsed = {
                "temp": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "temp_min": main.get("temp_min"),
                "temp_max": main.get("temp_max"),
                "pressure": main.get("pressure"),
                "humidity": main.get("humidity"),
                "visibility": data.get("visibility"),
                "wind_speed": wind.get("speed"),
                "wind_deg": wind.get("deg"),
                "wind_gust": wind.get("gust"),
                "clouds": clouds.get("all"),
                "rain_1h": rain.get("1h"),
                "rain_3h": rain.get("3h"),
                "condition": weather.get("main"),
            }
            
            # Add timestamp and location info
            parsed["timestamp"] = datetime.fromtimestamp(data.get("dt", 0))
            parsed["location_name"] = data.get("name")
            parsed["sunrise"] = datetime.fromtimestamp(sys.get("sunrise", 0)) if sys.get("sunrise") else None
            parsed["sunset"] = datetime.fromtimestamp(sys.get("sunset", 0)) if sys.get("sunset") else None
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing weather response: {e}")
            return {}
    
    def parse_air_pollution_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OpenWeatherMap air pollution response to our format
        
        Args:
            data: Raw API response
        
        Returns:
            Parsed air quality data
        """
        try:
            list_data = data.get("list", [])
            if not list_data:
                return {}
            
            item = list_data[0]
            components = item.get("components", {})
            
            parsed = {
                "aqi": item.get("main", {}).get("aqi"),
                "co": components.get("co"),
                "no": components.get("no"),
                "no2": components.get("no2"),
                "o3": components.get("o3"),
                "so2": components.get("so2"),
                "pm2_5": components.get("pm2_5"),
                "pm10": components.get("pm10"),
                "nh3": components.get("nh3"),
            }
            
            parsed["timestamp"] = datetime.fromtimestamp(item.get("dt", 0))
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing air pollution response: {e}")
            return {}


class OpenAQClient:
    """
    Client for OpenAQ API v3
    
    OpenAQ provides real-time air quality data from monitoring stations.
    Flow: locations → sensors → measurements
    """
    
    BASE_URL = "https://api.openaq.org/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAQ_API_KEY
        if not self.api_key:
            logger.warning("OpenAQ API key not configured. Some features may be limited.")
    
    async def get_locations_near(
        self,
        lat: float,
        lon: float,
        radius: int = 25000,
        limit: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Find monitoring locations near coordinates
        
        Example: GET /locations?coordinates=21.0285,105.8542&radius=25000&limit=100
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius in meters (max 25000)
            limit: Max number of results
        
        Returns:
            Locations data or None if error
        """
        try:
            url = f"{self.BASE_URL}/locations"
            
            params = {
                "coordinates": f"{lat},{lon}",
                "radius": min(radius, 25000),  # Max 25km
                "limit": limit
            }
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error finding OpenAQ locations: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error finding OpenAQ locations: {e}")
            return None
    
    async def get_location_detail(
        self,
        location_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get location details including sensors
        
        Example: GET /locations/4946811
        Returns location info + all sensors (PM2.5, PM10, CO, NO2, O3, SO2)
        
        Args:
            location_id: OpenAQ location ID
        
        Returns:
            Location data with sensors or None if error
        """
        try:
            url = f"{self.BASE_URL}/locations/{location_id}"
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting OpenAQ location: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error getting OpenAQ location: {e}")
            return None
    
    async def get_sensor_measurements(
        self,
        sensor_id: int,
        limit: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get measurements from a specific sensor
        
        Example: GET /sensors/13502150/measurements?limit=10
        
        Args:
            sensor_id: Sensor ID (e.g., 13502150 for PM2.5)
            limit: Number of measurements to return
            date_from: Start date (ISO format: 2025-11-25T00:00:00Z)
            date_to: End date (ISO format)
        
        Returns:
            Measurements data or None if error
        """
        try:
            url = f"{self.BASE_URL}/sensors/{sensor_id}/measurements"
            
            params = {"limit": limit}
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting sensor measurements: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error getting sensor measurements: {e}")
            return None
    
    def parse_location_sensors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse location detail response to extract sensor IDs
        
        Example response:
        {
          "results": [{
            "id": 4946811,
            "name": "556 Nguyễn Văn Cừ",
            "coordinates": {"latitude": 21.0285, "longitude": 105.8542},
            "sensors": [
              {"id": 13502150, "parameter": {"name": "pm25"}},
              {"id": 13502165, "parameter": {"name": "pm10"}},
              ...
            ]
          }]
        }
        
        Args:
            data: Raw API response from /locations/{id}
        
        Returns:
            Parsed location with sensor IDs
        """
        try:
            if not data or "results" not in data:
                return {}
            
            result = data["results"][0] if data["results"] else {}
            
            # Extract sensor IDs by parameter
            sensors_by_param = {}
            for sensor in result.get("sensors", []):
                param_name = sensor.get("parameter", {}).get("name", "").lower()
                sensor_id = sensor.get("id")
                
                if param_name and sensor_id:
                    # Map to our format
                    param_map = {
                        "pm25": "pm2_5",
                        "pm10": "pm10",
                        "o3": "o3",
                        "no2": "no2",
                        "so2": "so2",
                        "co": "co"
                    }
                    mapped_name = param_map.get(param_name, param_name)
                    sensors_by_param[mapped_name] = sensor_id
            
            coords = result.get("coordinates", {})
            
            return {
                "location_id": result.get("id"),
                "location_name": result.get("name"),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
                "sensors": sensors_by_param  # {"pm2_5": 13502150, "pm10": 13502165, ...}
            }
            
        except Exception as e:
            logger.error(f"Error parsing OpenAQ location: {e}")
            return {}
    
    def parse_sensor_measurements(self, data: Dict[str, Any], parameter: str) -> List[Dict[str, Any]]:
        """
        Parse sensor measurements response
        
        Example response:
        {
          "results": [
            {
              "value": 25.4,
              "datetime": "2025-11-26T10:00:00Z",
              "coordinates": {"latitude": 21.0285, "longitude": 105.8542}
            }
          ]
        }
        
        Args:
            data: Raw API response from /sensors/{id}/measurements
            parameter: Parameter name (pm2_5, pm10, etc.)
        
        Returns:
            List of measurements with timestamps
        """
        try:
            results = data.get("results", [])
            measurements = []
            
            for result in results:
                value = result.get("value")
                timestamp_str = result.get("datetime")
                
                if value is not None and timestamp_str:
                    measurements.append({
                        "parameter": parameter,
                        "value": value,
                        "timestamp": datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    })
            
            return measurements
            
        except Exception as e:
            logger.error(f"Error parsing sensor measurements: {e}")
            return []


    async def get_all_measurements_for_location(
        self,
        location_id: int,
        limit: int = 1
    ) -> Dict[str, Any]:
        """
        Get latest measurements from all sensors at a location
        
        Flow:
        1. GET /locations/{location_id} → Get sensor IDs
        2. For each sensor: GET /sensors/{sensor_id}/measurements?limit=1
        3. Combine all measurements
        
        Args:
            location_id: OpenAQ location ID
            limit: Number of measurements per sensor (default 1 = latest)
        
        Returns:
            Combined measurements from all sensors
        """
        try:
            # Step 1: Get location details with sensor IDs
            location_data = await self.get_location_detail(location_id)
            if not location_data:
                return {}
            
            parsed_location = self.parse_location_sensors(location_data)
            if not parsed_location or not parsed_location.get("sensors"):
                return {}
            
            # Step 2: Fetch measurements from each sensor
            measurements = {}
            for param, sensor_id in parsed_location["sensors"].items():
                sensor_data = await self.get_sensor_measurements(sensor_id, limit=limit)
                if sensor_data:
                    parsed_measurements = self.parse_sensor_measurements(sensor_data, param)
                    if parsed_measurements:
                        # Get latest measurement
                        latest = parsed_measurements[0]
                        measurements[param] = latest["value"]
            
            return {
                "location_id": parsed_location["location_id"],
                "location_name": parsed_location["location_name"],
                "latitude": parsed_location["latitude"],
                "longitude": parsed_location["longitude"],
                "measurements": measurements,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting all measurements for location {location_id}: {e}")
            return {}


# Singleton instances
openweather_client = OpenWeatherMapClient()
openaq_client = OpenAQClient()


async def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch weather and air quality data for a location
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Combined weather and air quality data
    """
    result = {
        "weather": None,
        "air_quality": None,
        "timestamp": datetime.utcnow()
    }
    
    # Fetch weather
    weather_data = await openweather_client.get_current_weather(lat, lon)
    if weather_data:
        result["weather"] = openweather_client.parse_weather_response(weather_data)
    
    # Fetch air pollution
    pollution_data = await openweather_client.get_air_pollution(lat, lon)
    if pollution_data:
        result["air_quality"] = openweather_client.parse_air_pollution_response(pollution_data)
    
    return result


async def fetch_openaq_data(lat: float, lon: float, radius: int = 25000) -> List[Dict[str, Any]]:
    """
    Fetch OpenAQ data from nearby monitoring stations
    
    Flow:
    1. Find locations near coordinates
    2. For each location, get all sensor measurements
    
    Args:
        lat: Latitude
        lon: Longitude
        radius: Search radius in meters (default 25km)
    
    Returns:
        List of measurements from nearby stations
    """
    try:
        # Step 1: Find nearby locations
        locations_data = await openaq_client.get_locations_near(lat, lon, radius, limit=10)
        
        if not locations_data or "results" not in locations_data:
            return []
        
        # Step 2: Get measurements from each location
        all_measurements = []
        
        for location in locations_data["results"]:
            location_id = location.get("id")
            if not location_id:
                continue
            
            # Get all measurements for this location
            measurements = await openaq_client.get_all_measurements_for_location(location_id, limit=1)
            
            if measurements and measurements.get("measurements"):
                all_measurements.append(measurements)
        
        return all_measurements
        
    except Exception as e:
        logger.error(f"Error fetching OpenAQ data: {e}")
        return []


async def fetch_openaq_location_by_id(location_id: int) -> Dict[str, Any]:
    """
    Fetch OpenAQ data from a specific location ID
    
    Example location IDs:
    - Hà Nội: 4946811, 4946812, 4946813, 6123215, 2161292
    - TP.HCM: 3276359, 6068138
    
    Args:
        location_id: OpenAQ location ID
    
    Returns:
        Measurements from all sensors at location
    """
    return await openaq_client.get_all_measurements_for_location(location_id, limit=1)


