# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

import httpx
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from app.core.config import settings
from app.adapters.sosa_helpers import create_weather_observations_from_owm

class OpenWeatherMapAdapter:
    """
    Adapter to fetch weather data from OpenWeatherMap API
    and convert it to NGSI-LD format.
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required")
    
    async def fetch_weather(self, lat: float, lon: float, city_name: str = "Unknown") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch current weather data for a location and convert to NGSI-LD Entity.
        
        Returns:
            Tuple of (WeatherObserved entity, List of SOSA Observation entities)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        
        # Convert to NGSI-LD format (legacy)
        entity_id = f"urn:ngsi-ld:WeatherObserved:{city_name.replace(' ', '')}:{int(datetime.now().timestamp())}"
        
        ngsi_ld_entity = {
            "id": entity_id,
            "type": "WeatherObserved",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Weather/master/context.jsonld"
            ],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            },
            "temperature": {
                "type": "Property",
                "value": data["main"]["temp"],
                "unitCode": "CEL",
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "humidity": {
                "type": "Property",
                "value": data["main"]["humidity"],
                "unitCode": "P1",
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "pressure": {
                "type": "Property",
                "value": data["main"]["pressure"],
                "unitCode": "A97",
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "windSpeed": {
                "type": "Property",
                "value": data["wind"]["speed"],
                "unitCode": "MTS",
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "weatherType": {
                "type": "Property",
                "value": data["weather"][0]["main"],
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "description": {
                "type": "Property",
                "value": data["weather"][0]["description"],
                "observedAt": datetime.utcnow().isoformat() + "Z"
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": city_name,
                    "addressCountry": "VN"
                }
            }
        }
        
        # Create SOSA observations
        sosa_observations = create_weather_observations_from_owm(data, city_name.lower())
        
        return ngsi_ld_entity, sosa_observations
    
    async def fetch_air_quality(self, lat: float, lon: float, city_name: str = "Unknown") -> Dict[str, Any]:
        """
        Fetch air quality data and convert to NGSI-LD Entity.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/air_pollution",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        
        if not data.get("list"):
            return None
        
        aqi_data = data["list"][0]
        entity_id = f"urn:ngsi-ld:AirQualityObserved:{city_name.replace(' ', '')}:{int(datetime.now().timestamp())}"
        
        ngsi_ld_entity = {
            "id": entity_id,
            "type": "AirQualityObserved",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
            ],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            },
            "aqi": {
                "type": "Property",
                "value": aqi_data["main"]["aqi"],
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "co": {
                "type": "Property",
                "value": aqi_data["components"].get("co", 0),
                "unitCode": "GP",
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "no2": {
                "type": "Property",
                "value": aqi_data["components"].get("no2", 0),
                "unitCode": "GP",
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "o3": {
                "type": "Property",
                "value": aqi_data["components"].get("o3", 0),
                "unitCode": "GP",
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "pm10": {
                "type": "Property",
                "value": aqi_data["components"].get("pm10", 0),
                "unitCode": "GQ",
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "pm25": {
                "type": "Property",
                "value": aqi_data["components"].get("pm2_5", 0),
                "unitCode": "GQ",
                "observedAt": datetime.utcfromtimestamp(aqi_data["dt"]).isoformat() + "Z"
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": city_name,
                    "addressCountry": "VN"
                }
            }
        }
        
        return ngsi_ld_entity

