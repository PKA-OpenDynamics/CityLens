"""
AQICN (WAQI) API Adapter - Real-time Air Quality Data
World Air Quality Index - https://aqicn.org/

Provides real-time air quality data from government monitoring stations worldwide.
Data is fresh, standardized, and covers major cities including Vietnam.
"""
import httpx
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from app.core.config import settings
from app.adapters.sosa_helpers import create_aqi_observations_from_aqicn


class AQICNAdapter:
    """
    Adapter to fetch real-time air quality data from AQICN (WAQI) API.
    Converts data to NGSI-LD AirQualityObserved entities.
    
    API Documentation: https://aqicn.org/api/
    Data Platform: https://aqicn.org/data-platform/api/
    """
    
    BASE_URL = "https://api.waqi.info"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.AQICN_API_KEY
        if not self.api_key:
            raise ValueError("AQICN API key is required")
    
    async def fetch_city_data(self, city: str = "hanoi") -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch air quality data for a specific city.
        
        Args:
            city: City name (e.g., "hanoi", "saigon", "danang")
        
        Returns:
            Tuple of (AirQualityObserved entity, List of SOSA Observation entities)
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/feed/{city}/",
                params={"token": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError(f"AQICN API error: {data.get('data', 'Unknown error')}")
        
        # Create both legacy entity and SOSA observations
        legacy_entity = self._convert_to_ngsi_ld(data["data"], city)
        sosa_observations = create_aqi_observations_from_aqicn(data["data"], city)
        
        return legacy_entity, sosa_observations
    
    async def fetch_station_data(self, station_id: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch air quality data from a specific monitoring station.
        
        Args:
            station_id: Station ID (e.g., "H13026" for Hanoi station)
        
        Returns:
            Tuple of (AirQualityObserved entity, List of SOSA Observation entities)
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/feed/@{station_id}/",
                params={"token": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError(f"AQICN API error: {data.get('data', 'Unknown error')}")
        
        # Create both legacy entity and SOSA observations
        legacy_entity = self._convert_to_ngsi_ld(data["data"], station_id=station_id)
        sosa_observations = create_aqi_observations_from_aqicn(data["data"])
        
        return legacy_entity, sosa_observations
    
    async def fetch_geo_data(self, lat: float, lon: float) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch air quality data for nearest station to given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Tuple of (AirQualityObserved entity, List of SOSA Observation entities)
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/feed/geo:{lat};{lon}/",
                params={"token": self.api_key}
            )
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError(f"AQICN API error: {data.get('data', 'Unknown error')}")
        
        # Create both legacy entity and SOSA observations
        legacy_entity = self._convert_to_ngsi_ld(data["data"], city=f"Geo_{lat}_{lon}")
        sosa_observations = create_aqi_observations_from_aqicn(data["data"])
        
        return legacy_entity, sosa_observations
    
    async def fetch_multiple_cities(self, cities: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch air quality data for multiple cities.
        
        Args:
            cities: List of city names
        
        Returns:
            List of NGSI-LD AirQualityObserved entities
        """
        entities = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for city in cities:
                try:
                    response = await client.get(
                        f"{self.BASE_URL}/feed/{city}/",
                        params={"token": self.api_key}
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("status") == "ok":
                        entity = self._convert_to_ngsi_ld(data["data"], city)
                        entities.append(entity)
                except:
                    # Skip failed cities
                    continue
        
        return entities
    
    def _convert_to_ngsi_ld(
        self, 
        data: Dict[str, Any],
        city: Optional[str] = None,
        station_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert AQICN data to NGSI-LD AirQualityObserved entity.
        
        AQICN response structure:
        {
            "aqi": 42,  # Overall AQI
            "idx": 10406,  # Station ID
            "city": {"name": "Hanoi, Vietnam", "geo": [21.0278, 105.8342]},
            "time": {"s": "2025-12-03 10:00:00", "tz": "+07:00", "v": 1733223600},
            "iaqi": {  # Individual pollutants
                "pm25": {"v": 10.5},
                "pm10": {"v": 20},
                "o3": {"v": 30},
                "no2": {"v": 15},
                "so2": {"v": 5},
                "co": {"v": 0.3}
            }
        }
        """
        # Extract location info
        station_idx = data.get("idx", "unknown")
        city_info = data.get("city", {})
        city_name = city_info.get("name", city or "Unknown")
        geo = city_info.get("geo", [])
        
        if len(geo) >= 2:
            lat, lon = geo[0], geo[1]
        else:
            lat, lon = None, None
        
        # Create entity ID
        city_clean = city_name.replace(" ", "").replace(",", "_")
        if station_id:
            entity_id = f"urn:ngsi-ld:AirQualityObserved:AQICN:{station_id}"
        else:
            entity_id = f"urn:ngsi-ld:AirQualityObserved:AQICN:{city_clean}:{station_idx}"
        
        # Extract timestamp
        time_info = data.get("time", {})
        observed_time = time_info.get("s", "")
        if observed_time:
            try:
                # Convert "2025-12-03 10:00:00" to ISO 8601
                dt = datetime.strptime(observed_time, "%Y-%m-%d %H:%M:%S")
                tz = time_info.get("tz", "+00:00")
                observed_at = dt.isoformat() + tz.replace("+", "+").replace("-", "-")
            except:
                observed_at = datetime.utcnow().isoformat() + "Z"
        else:
            observed_at = datetime.utcnow().isoformat() + "Z"
        
        # Build NGSI-LD entity
        entity = {
            "id": entity_id,
            "type": "AirQualityObserved",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Environment/master/context.jsonld"
            ],
            "dateObserved": {
                "type": "Property",
                "value": observed_at
            },
            "source": {
                "type": "Property",
                "value": "AQICN/WAQI"
            },
            "refPointOfInterest": {
                "type": "Property",
                "value": f"https://aqicn.org/station/@{station_idx}/"
            }
        }
        
        # Add location if available
        if lat is not None and lon is not None:
            entity["location"] = {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        
        # Add address/city name
        entity["address"] = {
            "type": "Property",
            "value": {
                "addressLocality": city_name,
                "addressCountry": self._extract_country(city_name)
            }
        }
        
        # Add AQI (overall air quality index)
        aqi_value = data.get("aqi")
        if aqi_value and aqi_value != "-":
            entity["airQualityIndex"] = {
                "type": "Property",
                "value": int(aqi_value) if isinstance(aqi_value, (int, float)) else aqi_value,
                "observedAt": observed_at
            }
        
        # Add individual pollutant measurements (iaqi)
        iaqi = data.get("iaqi", {})
        
        # PM2.5
        if "pm25" in iaqi:
            entity["pm25"] = {
                "type": "Property",
                "value": iaqi["pm25"].get("v"),
                "unitCode": "GQ",  # µg/m³
                "observedAt": observed_at
            }
        
        # PM10
        if "pm10" in iaqi:
            entity["pm10"] = {
                "type": "Property",
                "value": iaqi["pm10"].get("v"),
                "unitCode": "GQ",  # µg/m³
                "observedAt": observed_at
            }
        
        # O3 (Ozone)
        if "o3" in iaqi:
            entity["o3"] = {
                "type": "Property",
                "value": iaqi["o3"].get("v"),
                "unitCode": "GQ",  # µg/m³
                "observedAt": observed_at
            }
        
        # NO2 (Nitrogen Dioxide)
        if "no2" in iaqi:
            entity["no2"] = {
                "type": "Property",
                "value": iaqi["no2"].get("v"),
                "unitCode": "GQ",  # µg/m³
                "observedAt": observed_at
            }
        
        # SO2 (Sulfur Dioxide)
        if "so2" in iaqi:
            entity["so2"] = {
                "type": "Property",
                "value": iaqi["so2"].get("v"),
                "unitCode": "GQ",  # µg/m³
                "observedAt": observed_at
            }
        
        # CO (Carbon Monoxide)
        if "co" in iaqi:
            entity["co"] = {
                "type": "Property",
                "value": iaqi["co"].get("v"),
                "unitCode": "GP",  # mg/m³
                "observedAt": observed_at
            }
        
        return entity
    
    def _extract_country(self, city_name: str) -> str:
        """Extract country from city name string."""
        if "," in city_name:
            parts = city_name.split(",")
            if len(parts) > 1:
                return parts[-1].strip()
        
        # Default mapping for common cities
        city_lower = city_name.lower()
        if any(x in city_lower for x in ["hanoi", "saigon", "danang", "vietnam"]):
            return "Vietnam"
        elif any(x in city_lower for x in ["jakarta", "indonesia"]):
            return "Indonesia"
        elif any(x in city_lower for x in ["bangkok", "thailand"]):
            return "Thailand"
        
        return "Unknown"
