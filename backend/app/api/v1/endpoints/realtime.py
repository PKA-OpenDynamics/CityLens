# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Realtime Data API Endpoints (Layer 2: Urban Infrastructure)

Provides real-time environmental and urban data including:
- Weather observations from OpenWeatherMap API
- Air quality index (AQI) from WAQI/AQICN API
- Traffic flow from TomTom API

All data is returned in NGSI-LD compatible format for Smart City integration.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Default coordinates for Hanoi
DEFAULT_LAT = 21.028511
DEFAULT_LON = 105.804817


def _get_aqi_level(aqi_value: int) -> Dict[str, str]:
    """Get AQI level description based on value."""
    if aqi_value <= 50:
        return {
            "level": "Good",
            "color": "#00E400",
            "description": "Air quality is satisfactory, and air pollution poses little or no risk.",
            "health_implications": "None"
        }
    elif aqi_value <= 100:
        return {
            "level": "Moderate",
            "color": "#FFFF00",
            "description": "Air quality is acceptable. However, there may be a risk for some people.",
            "health_implications": "Unusually sensitive people should consider reducing prolonged outdoor exertion."
        }
    elif aqi_value <= 150:
        return {
            "level": "Unhealthy for Sensitive Groups",
            "color": "#FF7E00",
            "description": "Members of sensitive groups may experience health effects.",
            "health_implications": "Active children and adults, and people with respiratory disease, should limit prolonged outdoor exertion."
        }
    elif aqi_value <= 200:
        return {
            "level": "Unhealthy",
            "color": "#FF0000",
            "description": "Everyone may begin to experience health effects.",
            "health_implications": "Active children and adults should avoid prolonged outdoor exertion."
        }
    elif aqi_value <= 300:
        return {
            "level": "Very Unhealthy",
            "color": "#8F3F97",
            "description": "Health alert: everyone may experience more serious health effects.",
            "health_implications": "Everyone should avoid all outdoor exertion."
        }
    else:
        return {
            "level": "Hazardous",
            "color": "#7E0023",
            "description": "Health warnings of emergency conditions.",
            "health_implications": "Everyone should avoid all outdoor activity."
        }


@router.get("/weather/latest")
async def get_latest_weather(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude coordinate"),
    city: Optional[str] = Query("Hanoi", description="City name for context"),
):
    """
    Get latest weather observation data from OpenWeatherMap API.
    
    Returns NGSI-LD compatible WeatherObserved entity.
    
    **Coordinates:** Default to Hanoi center (21.028511, 105.804817)
    """
    lat = latitude or DEFAULT_LAT
    lon = longitude or DEFAULT_LON
    
    # Check if API key is configured
    if not settings.OPENWEATHER_API_KEY:
        logger.warning("OpenWeatherMap API key not configured, returning stub data")
        return _get_weather_stub(lat, lon, city)
    
    try:
        from app.adapters.openweathermap import OpenWeatherMapAdapter
        adapter = OpenWeatherMapAdapter()
        ngsi_ld_entity, sosa_observations = await adapter.fetch_weather(lat, lon, city)
        
        # Transform to frontend-friendly format
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "OpenWeatherMap",
            "ngsi_ld_entity": ngsi_ld_entity,
            "location": {
                "latitude": lat,
                "longitude": lon,
                "city": city,
                "country": "Vietnam"
            },
            "weather": {
                "temperature": ngsi_ld_entity.get("temperature", {}).get("value"),
                "feels_like": ngsi_ld_entity.get("feelsLikeTemperature", {}).get("value"),
                "humidity": ngsi_ld_entity.get("humidity", {}).get("value"),
                "pressure": ngsi_ld_entity.get("pressure", {}).get("value"),
                "description": ngsi_ld_entity.get("description", {}).get("value"),
                "wind_speed": ngsi_ld_entity.get("windSpeed", {}).get("value"),
                "clouds": ngsi_ld_entity.get("clouds", {}).get("value"),
                "visibility": ngsi_ld_entity.get("visibility", {}).get("value")
            }
        }
        
    except ValueError as e:
        logger.warning(f"Weather API error: {e}")
        return _get_weather_stub(lat, lon, city)
    except Exception as e:
        logger.error(f"Unexpected error fetching weather: {e}")
        return _get_weather_stub(lat, lon, city)


def _get_weather_stub(lat: float, lon: float, city: str) -> Dict[str, Any]:
    """Return stub weather data when API is unavailable."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "stub",
        "api_status": "API key not configured or unavailable",
        "location": {
            "latitude": lat,
            "longitude": lon,
            "city": city,
            "country": "Vietnam"
        },
        "weather": {
            "temperature": 28.5,
            "feels_like": 30.2,
            "humidity": 75,
            "pressure": 1012,
            "description": "Partly cloudy",
            "icon": "02d",
            "wind_speed": 3.5,
            "wind_direction": 180,
            "clouds": 40,
            "visibility": 10000
        }
    }


@router.get("/air-quality/latest")
async def get_latest_air_quality(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude coordinate"),
    city: Optional[str] = Query("hanoi", description="City name for AQICN lookup"),
):
    """
    Get latest air quality index (AQI) data from AQICN/WAQI API.
    
    Returns NGSI-LD compatible AirQualityObserved entity.
    
    **Data source:** WAQI (World Air Quality Index) - https://aqicn.org/
    
    **Supported cities:** hanoi, saigon, danang, haiphong, etc.
    """
    lat = latitude or DEFAULT_LAT
    lon = longitude or DEFAULT_LON
    
    # Check if API key is configured
    if not settings.AQICN_API_KEY:
        logger.warning("AQICN API key not configured, returning stub data")
        return _get_aqi_stub(lat, lon, city)
    
    try:
        from app.adapters.aqicn import AQICNAdapter
        adapter = AQICNAdapter()
        
        # Try city-based lookup first, then geo-based
        try:
            ngsi_ld_entity, sosa_observations = await adapter.fetch_city_data(city)
        except:
            ngsi_ld_entity, sosa_observations = await adapter.fetch_geo_data(lat, lon)
        
        # Extract AQI value
        aqi_value = ngsi_ld_entity.get("airQualityIndex", {}).get("value", 0)
        aqi_info = _get_aqi_level(int(aqi_value) if aqi_value else 0)
        
        # Transform to frontend-friendly format
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "AQICN/WAQI",
            "ngsi_ld_entity": ngsi_ld_entity,
            "location": {
                "latitude": ngsi_ld_entity.get("location", {}).get("value", {}).get("coordinates", [lon, lat])[1],
                "longitude": ngsi_ld_entity.get("location", {}).get("value", {}).get("coordinates", [lon, lat])[0],
                "city": city.title(),
                "country": "Vietnam",
                "station": ngsi_ld_entity.get("refPointOfInterest", {}).get("value", "")
            },
            "aqi": {
                "value": aqi_value,
                **aqi_info
            },
            "pollutants": {
                "pm25": {
                    "value": ngsi_ld_entity.get("pm25", {}).get("value"),
                    "unit": "µg/m³",
                    "description": "Fine particulate matter (PM2.5)"
                },
                "pm10": {
                    "value": ngsi_ld_entity.get("pm10", {}).get("value"),
                    "unit": "µg/m³",
                    "description": "Coarse particulate matter (PM10)"
                },
                "o3": {
                    "value": ngsi_ld_entity.get("o3", {}).get("value"),
                    "unit": "µg/m³",
                    "description": "Ozone (O₃)"
                },
                "no2": {
                    "value": ngsi_ld_entity.get("no2", {}).get("value"),
                    "unit": "µg/m³",
                    "description": "Nitrogen dioxide (NO₂)"
                },
                "so2": {
                    "value": ngsi_ld_entity.get("so2", {}).get("value"),
                    "unit": "µg/m³",
                    "description": "Sulfur dioxide (SO₂)"
                },
                "co": {
                    "value": ngsi_ld_entity.get("co", {}).get("value"),
                    "unit": "mg/m³",
                    "description": "Carbon monoxide (CO)"
                }
            }
        }
        
    except ValueError as e:
        logger.warning(f"AQI API error: {e}")
        return _get_aqi_stub(lat, lon, city)
    except Exception as e:
        logger.error(f"Unexpected error fetching AQI: {e}")
        return _get_aqi_stub(lat, lon, city)


def _get_aqi_stub(lat: float, lon: float, city: str) -> Dict[str, Any]:
    """Return stub AQI data when API is unavailable."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "stub",
        "api_status": "API key not configured or unavailable",
        "location": {
            "latitude": lat,
            "longitude": lon,
            "city": city.title(),
            "country": "Vietnam",
            "station": "Stub Station"
        },
        "aqi": {
            "value": 85,
            "level": "Moderate",
            "color": "#FFFF00",
            "description": "Air quality is acceptable for most people.",
            "health_implications": "Unusually sensitive people should consider reducing prolonged outdoor exertion."
        },
        "pollutants": {
            "pm25": {"value": 28.5, "unit": "µg/m³", "description": "Fine particulate matter"},
            "pm10": {"value": 45.2, "unit": "µg/m³", "description": "Coarse particulate matter"},
            "o3": {"value": 35.0, "unit": "µg/m³", "description": "Ozone"},
            "no2": {"value": 20.5, "unit": "µg/m³", "description": "Nitrogen dioxide"},
            "so2": {"value": 8.2, "unit": "µg/m³", "description": "Sulfur dioxide"},
            "co": {"value": 0.4, "unit": "mg/m³", "description": "Carbon monoxide"}
        }
    }


@router.get("/traffic/latest")
async def get_latest_traffic(
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude coordinate"),
    location_name: Optional[str] = Query("Hanoi Center", description="Location name for context"),
):
    """
    Get latest traffic flow data from TomTom Traffic API.
    
    Returns NGSI-LD compatible TrafficFlowObserved entity.
    
    **Data includes:** current speed, free flow speed, congestion level, travel time
    """
    lat = latitude or DEFAULT_LAT
    lon = longitude or DEFAULT_LON
    
    # Check if API key is configured
    if not settings.TOMTOM_API_KEY:
        logger.warning("TomTom API key not configured, returning stub data")
        return _get_traffic_stub(lat, lon, location_name)
    
    try:
        from app.adapters.tomtom import TomTomAdapter
        adapter = TomTomAdapter()
        ngsi_ld_entity = await adapter.fetch_traffic_flow(lat, lon, location_name=location_name)
        
        # Calculate congestion level
        current_speed = ngsi_ld_entity.get("averageVehicleSpeed", {}).get("value", 0)
        free_flow_speed = ngsi_ld_entity.get("freeFlowSpeed", {}).get("value", 1)
        
        if free_flow_speed > 0:
            speed_ratio = current_speed / free_flow_speed
            if speed_ratio >= 0.9:
                congestion_level = "free_flow"
            elif speed_ratio >= 0.7:
                congestion_level = "light"
            elif speed_ratio >= 0.5:
                congestion_level = "moderate"
            elif speed_ratio >= 0.3:
                congestion_level = "heavy"
            else:
                congestion_level = "severe"
        else:
            congestion_level = "unknown"
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "TomTom",
            "ngsi_ld_entity": ngsi_ld_entity,
            "location": {
                "latitude": lat,
                "longitude": lon,
                "name": location_name
            },
            "traffic": {
                "current_speed": current_speed,
                "free_flow_speed": free_flow_speed,
                "congestion_level": congestion_level,
                "travel_time": ngsi_ld_entity.get("travelTime", {}).get("value"),
                "confidence": ngsi_ld_entity.get("confidence", {}).get("value", 0.85),
                "road_class": ngsi_ld_entity.get("roadClass", {}).get("value")
            }
        }
        
    except ValueError as e:
        logger.warning(f"Traffic API error: {e}")
        return _get_traffic_stub(lat, lon, location_name)
    except Exception as e:
        logger.error(f"Unexpected error fetching traffic: {e}")
        return _get_traffic_stub(lat, lon, location_name)


def _get_traffic_stub(lat: float, lon: float, location_name: str) -> Dict[str, Any]:
    """Return stub traffic data when API is unavailable."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "stub",
        "api_status": "API key not configured or unavailable",
        "location": {
            "latitude": lat,
            "longitude": lon,
            "name": location_name
        },
        "traffic": {
            "current_speed": 25.5,
            "free_flow_speed": 50.0,
            "congestion_level": "moderate",
            "travel_time": 120,
            "confidence": 0.85,
            "road_class": "FRC4"
        }
    }


@router.get("/weather/cities")
async def get_weather_multiple_cities(
    cities: str = Query(
        "hanoi,saigon,danang",
        description="Comma-separated list of city names"
    )
):
    """
    Get weather data for multiple Vietnamese cities.
    
    **Supported cities:** hanoi, saigon, danang, haiphong, cantho, nhatrang, dalat, hue
    """
    city_coords = {
        "hanoi": (21.028511, 105.804817),
        "saigon": (10.762622, 106.660172),
        "hochiminh": (10.762622, 106.660172),
        "danang": (16.047079, 108.206230),
        "haiphong": (20.844912, 106.688084),
        "cantho": (10.045162, 105.746857),
        "nhatrang": (12.238791, 109.196749),
        "dalat": (11.940419, 108.458313),
        "hue": (16.463713, 107.590866),
    }
    
    city_list = [c.strip().lower() for c in cities.split(",")]
    results = []
    
    for city in city_list:
        coords = city_coords.get(city)
        if coords:
            try:
                weather = await get_latest_weather(coords[0], coords[1], city.title())
                results.append(weather)
            except:
                pass
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "count": len(results),
        "cities": results
    }


@router.get("/air-quality/cities")
async def get_aqi_multiple_cities(
    cities: str = Query(
        "hanoi,saigon,danang",
        description="Comma-separated list of city names"
    )
):
    """
    Get AQI data for multiple Vietnamese cities.
    
    **Supported cities:** hanoi, saigon, danang, haiphong, and more from AQICN network
    """
    city_list = [c.strip().lower() for c in cities.split(",")]
    
    if not settings.AQICN_API_KEY:
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "stub",
            "api_status": "API key not configured",
            "count": 0,
            "cities": []
        }
    
    try:
        from app.adapters.aqicn import AQICNAdapter
        adapter = AQICNAdapter()
        entities = await adapter.fetch_multiple_cities(city_list)
        
        results = []
        for entity in entities:
            aqi_value = entity.get("airQualityIndex", {}).get("value", 0)
            aqi_info = _get_aqi_level(int(aqi_value) if aqi_value else 0)
            
            results.append({
                "city": entity.get("address", {}).get("value", {}).get("addressLocality", "Unknown"),
                "aqi": {
                    "value": aqi_value,
                    **aqi_info
                },
                "location": entity.get("location", {}).get("value", {}),
                "observed_at": entity.get("dateObserved", {}).get("value")
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "AQICN/WAQI",
            "count": len(results),
            "cities": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching multi-city AQI: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error",
            "error": str(e),
            "count": 0,
            "cities": []
        }


@router.get("/traffic/hotspots")
async def get_traffic_hotspots():
    """
    Get traffic data for known traffic hotspots in Hanoi.
    
    Returns traffic conditions at major intersections and busy roads.
    """
    hotspots = [
        {"name": "Ngã Tư Sở", "lat": 21.0009, "lon": 105.8210},
        {"name": "Cầu Giấy", "lat": 21.0367, "lon": 105.7946},
        {"name": "Trần Duy Hưng", "lat": 21.0137, "lon": 105.7996},
        {"name": "Hồ Hoàn Kiếm", "lat": 21.0285, "lon": 105.8542},
        {"name": "Long Biên Bridge", "lat": 21.0441, "lon": 105.8611},
        {"name": "Giảng Võ", "lat": 21.0245, "lon": 105.8257},
        {"name": "Kim Mã", "lat": 21.0308, "lon": 105.8177},
        {"name": "Đại Cồ Việt", "lat": 21.0025, "lon": 105.8484},
    ]
    
    if not settings.TOMTOM_API_KEY:
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "stub",
            "api_status": "API key not configured",
            "count": len(hotspots),
            "hotspots": [
                {
                    "name": h["name"],
                    "location": {"latitude": h["lat"], "longitude": h["lon"]},
                    "traffic": {
                        "current_speed": 20 + (i * 3) % 25,
                        "free_flow_speed": 50,
                        "congestion_level": ["light", "moderate", "heavy"][i % 3]
                    }
                }
                for i, h in enumerate(hotspots)
            ]
        }
    
    try:
        from app.adapters.tomtom import TomTomAdapter
        adapter = TomTomAdapter()
        
        results = []
        for hotspot in hotspots:
            try:
                entity = await adapter.fetch_traffic_flow(
                    hotspot["lat"], 
                    hotspot["lon"],
                    location_name=hotspot["name"]
                )
                
                current_speed = entity.get("averageVehicleSpeed", {}).get("value", 0)
                free_flow_speed = entity.get("freeFlowSpeed", {}).get("value", 50)
                
                if free_flow_speed > 0:
                    ratio = current_speed / free_flow_speed
                    congestion = "free_flow" if ratio >= 0.9 else "light" if ratio >= 0.7 else "moderate" if ratio >= 0.5 else "heavy" if ratio >= 0.3 else "severe"
                else:
                    congestion = "unknown"
                
                results.append({
                    "name": hotspot["name"],
                    "location": {"latitude": hotspot["lat"], "longitude": hotspot["lon"]},
                    "traffic": {
                        "current_speed": current_speed,
                        "free_flow_speed": free_flow_speed,
                        "congestion_level": congestion
                    }
                })
            except:
                pass
        
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "TomTom",
            "count": len(results),
            "hotspots": results
        }
        
    except Exception as e:
        logger.error(f"Error fetching traffic hotspots: {e}")
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "error",
            "error": str(e),
            "count": 0,
            "hotspots": []
        }
