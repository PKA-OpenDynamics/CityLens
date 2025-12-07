# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
TomTom API Adapter - Traffic & Places Data
https://developer.tomtom.com/

Provides:
1. Real-time traffic flow data (TrafficFlowObserved)
2. Traffic incidents (accidents, road closures, hazards)
3. POI search with commercial data (PointOfInterest)
4. Geocoding for address validation
"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.config import settings


class TomTomAdapter:
    """
    Adapter for TomTom APIs focusing on Traffic and Places data.
    Converts to NGSI-LD format for Smart City platform.
    """
    
    BASE_URL = "https://api.tomtom.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TOMTOM_API_KEY
        if not self.api_key:
            raise ValueError("TomTom API key is required")
    
    async def fetch_traffic_flow(
        self, 
        lat: float, 
        lon: float,
        zoom: int = 10,
        location_name: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Fetch real-time traffic flow data for a specific point.
        
        Args:
            lat: Latitude
            lon: Longitude
            zoom: Zoom level (10 = detailed street level)
            location_name: Name of the location for entity ID
        
        Returns:
            NGSI-LD TrafficFlowObserved entity
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/traffic/services/4/flowSegmentData/absolute/{zoom}/json",
                params={
                    "key": self.api_key,
                    "point": f"{lat},{lon}"
                }
            )
            response.raise_for_status()
            data = response.json()
        
        if "flowSegmentData" not in data:
            raise ValueError("No traffic flow data available")
        
        return self._convert_traffic_to_ngsi_ld(data["flowSegmentData"], lat, lon, location_name)
    
    async def fetch_multiple_traffic_points(
        self,
        points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fetch traffic data for multiple points.
        
        Args:
            points: List of dicts with keys: lat, lon, name
        
        Returns:
            List of NGSI-LD TrafficFlowObserved entities
        """
        entities = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for point in points:
                try:
                    response = await client.get(
                        f"{self.BASE_URL}/traffic/services/4/flowSegmentData/absolute/10/json",
                        params={
                            "key": self.api_key,
                            "point": f"{point['lat']},{point['lon']}"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if "flowSegmentData" in data:
                        entity = self._convert_traffic_to_ngsi_ld(
                            data["flowSegmentData"],
                            point["lat"],
                            point["lon"],
                            point.get("name", "Unknown")
                        )
                        entities.append(entity)
                except:
                    continue
        
        return entities
    
    async def search_pois(
        self,
        category: str,
        lat: float,
        lon: float,
        radius: int = 5000,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for Points of Interest by category.
        
        Args:
            category: POI category (e.g., "hospital", "restaurant", "school")
            lat: Center latitude
            lon: Center longitude
            radius: Search radius in meters (default 5km)
            limit: Maximum results (default 20)
        
        Returns:
            List of NGSI-LD PointOfInterest entities
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/search/2/categorySearch/{category}.json",
                params={
                    "key": self.api_key,
                    "lat": lat,
                    "lon": lon,
                    "radius": radius,
                    "limit": limit
                }
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for result in data.get("results", []):
            try:
                entity = self._convert_poi_to_ngsi_ld(result)
                entities.append(entity)
            except:
                continue
        
        return entities
    
    async def geocode_address(self, address: str) -> Dict[str, Any]:
        """
        Convert address to coordinates.
        
        Args:
            address: Address string (e.g., "Hoan Kiem, Hanoi")
        
        Returns:
            Dict with lat, lon, and formatted address
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/search/2/geocode/{address}.json",
                params={
                    "key": self.api_key,
                    "limit": 1
                }
            )
            response.raise_for_status()
            data = response.json()
        
        if not data.get("results"):
            raise ValueError(f"No geocoding results for address: {address}")
        
        result = data["results"][0]
        return {
            "lat": result["position"]["lat"],
            "lon": result["position"]["lon"],
            "address": result["address"].get("freeformAddress", address),
            "confidence": result.get("score", 0)
        }
    
    def _convert_traffic_to_ngsi_ld(
        self,
        flow_data: Dict[str, Any],
        lat: float,
        lon: float,
        location_name: str
    ) -> Dict[str, Any]:
        """
        Convert TomTom traffic flow data to NGSI-LD TrafficFlowObserved entity.
        
        TomTom structure:
        {
            "frc": "FRC4",  # Functional Road Class
            "currentSpeed": 24,  # km/h
            "freeFlowSpeed": 24,  # km/h without traffic
            "currentTravelTime": 204,  # seconds
            "freeFlowTravelTime": 204,
            "confidence": 1.0,  # 0-1
            "roadClosure": false
        }
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Calculate congestion level (0-100%)
        current_speed = flow_data.get("currentSpeed", 0)
        free_flow_speed = flow_data.get("freeFlowSpeed", current_speed)
        
        if free_flow_speed > 0:
            congestion = max(0, min(100, int((1 - current_speed / free_flow_speed) * 100)))
        else:
            congestion = 0
        
        # Create entity ID
        location_clean = location_name.replace(" ", "")
        entity_id = f"urn:ngsi-ld:TrafficFlowObserved:TomTom:{location_clean}:{int(lat*1000)}_{int(lon*1000)}"
        
        entity = {
            "id": entity_id,
            "type": "TrafficFlowObserved",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/master/context.jsonld"
            ],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            },
            "dateObserved": {
                "type": "Property",
                "value": timestamp
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": location_name
                }
            },
            "averageVehicleSpeed": {
                "type": "Property",
                "value": current_speed,
                "unitCode": "KMH",
                "observedAt": timestamp
            },
            "averageVehicleSpeedFreeFlow": {
                "type": "Property",
                "value": free_flow_speed,
                "unitCode": "KMH",
                "observedAt": timestamp
            },
            "congestionLevel": {
                "type": "Property",
                "value": congestion,
                "unitCode": "P1",  # Percentage
                "observedAt": timestamp
            },
            "travelTime": {
                "type": "Property",
                "value": flow_data.get("currentTravelTime", 0),
                "unitCode": "SEC",
                "observedAt": timestamp
            },
            "travelTimeFreeFlow": {
                "type": "Property",
                "value": flow_data.get("freeFlowTravelTime", 0),
                "unitCode": "SEC",
                "observedAt": timestamp
            },
            "dataProvider": {
                "type": "Property",
                "value": "TomTom Traffic API"
            },
            "confidence": {
                "type": "Property",
                "value": flow_data.get("confidence", 0),
                "observedAt": timestamp
            }
        }
        
        # Add road closure info if available
        if flow_data.get("roadClosure"):
            entity["roadClosed"] = {
                "type": "Property",
                "value": True,
                "observedAt": timestamp
            }
        
        return entity
    
    def _convert_poi_to_ngsi_ld(self, poi_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert TomTom POI to NGSI-LD PointOfInterest entity.
        
        TomTom structure:
        {
            "type": "POI",
            "id": "...",
            "poi": {
                "name": "Hospital Name",
                "phone": "+84...",
                "categories": ["hospital"],
                "categorySet": [{"id": 7321}]
            },
            "address": {...},
            "position": {"lat": ..., "lon": ...}
        }
        """
        poi = poi_data.get("poi", {})
        address = poi_data.get("address", {})
        position = poi_data.get("position", {})
        
        # Create entity ID from TomTom ID
        tomtom_id = poi_data.get("id", "unknown").replace("-", "")
        entity_id = f"urn:ngsi-ld:PointOfInterest:TomTom:{tomtom_id}"
        
        entity = {
            "id": entity_id,
            "type": "PointOfInterest",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.PointOfInterest/master/context.jsonld"
            ],
            "name": {
                "type": "Property",
                "value": poi.get("name", "Unknown")
            },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [position.get("lon"), position.get("lat")]
                }
            },
            "address": {
                "type": "Property",
                "value": {
                    "streetAddress": address.get("freeformAddress", ""),
                    "addressLocality": address.get("municipality", ""),
                    "addressCountry": address.get("countryCode", "")
                }
            },
            "category": {
                "type": "Property",
                "value": poi.get("categories", ["general"])
            },
            "source": {
                "type": "Property",
                "value": "TomTom Places API"
            }
        }
        
        # Add phone if available
        if poi.get("phone"):
            entity["contactPoint"] = {
                "type": "Property",
                "value": {
                    "telephone": poi["phone"]
                }
            }
        
        # Add distance if available
        if "dist" in poi_data:
            entity["distance"] = {
                "type": "Property",
                "value": round(poi_data["dist"], 2),
                "unitCode": "MTR"
            }
        
        return entity
    
    async def fetch_traffic_incidents(
        self,
        bbox: Dict[str, float],
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch traffic incidents (accidents, road closures, hazards) in a bounding box.
        
        TomTom Traffic Incidents API provides:
        - Accidents
        - Road closures
        - Construction work
        - Weather-related incidents
        - Dangerous conditions
        
        Args:
            bbox: Bounding box with keys: min_lat, min_lon, max_lat, max_lon
            severity: Filter by severity (0-4): 0=Unknown, 1=Minor, 2=Moderate, 3=Major, 4=Undefined
        
        Returns:
            List of NGSI-LD TrafficEvent entities
        
        API Docs: https://developer.tomtom.com/traffic-api/documentation/traffic-incidents/traffic-incident-details
        """
        bbox_str = f"{bbox['min_lon']},{bbox['min_lat']},{bbox['max_lon']},{bbox['max_lat']}"
        
        params = {
            "key": self.api_key,
            "bbox": bbox_str,
            "fields": "{incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code,iconCategory},startTime,endTime,from,to,length,delay,roadNumbers,timeValidity}}}",
            "language": "en-GB",
            "categoryFilter": "0,1,2,3,4,5,6,7,8,9,10,11,14",  # All incident categories
            "timeValidityFilter": "present"
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/traffic/services/5/incidentDetails",
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        incidents = data.get("incidents", [])
        
        # Filter by severity if specified
        if severity is not None:
            severity_int = int(severity)
            incidents = [inc for inc in incidents if inc.get("properties", {}).get("magnitudeOfDelay") == severity_int]
        
        # Convert to NGSI-LD
        entities = []
        for incident in incidents:
            try:
                entity = self._convert_incident_to_ngsi_ld(incident)
                entities.append(entity)
            except Exception as e:
                print(f"Error converting incident: {e}")
                continue
        
        return entities
    
    async def fetch_incidents_by_point(
        self,
        lat: float,
        lon: float,
        radius_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Fetch traffic incidents near a specific point.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Search radius in kilometers (default 5km)
        
        Returns:
            List of NGSI-LD TrafficEvent entities
        """
        # Calculate bounding box from point and radius
        # Approximate: 1 degree lat = 111km, 1 degree lon varies by latitude
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(lat))  # Rough approximation
        
        bbox = {
            "min_lat": lat - lat_offset,
            "max_lat": lat + lat_offset,
            "min_lon": lon - lon_offset,
            "max_lon": lon + lon_offset
        }
        
        return await self.fetch_traffic_incidents(bbox)
    
    def _convert_incident_to_ngsi_ld(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert TomTom incident to NGSI-LD TrafficEvent entity.
        
        TomTom Incident Categories:
        0 = Unknown, 1 = Accident, 2 = Fog, 3 = Dangerous Conditions, 4 = Rain
        5 = Ice, 6 = Jam, 7 = Lane Closed, 8 = Road Closed, 9 = Road Works
        10 = Wind, 11 = Flooding, 14 = Broken Down Vehicle
        """
        props = incident.get("properties", {})
        geometry = incident.get("geometry", {})
        
        incident_id = props.get("id", "unknown")
        entity_id = f"urn:ngsi-ld:TrafficEvent:TomTom:{incident_id}"
        
        # Map TomTom icon category to incident type
        icon_category = props.get("iconCategory", 0)
        incident_type_map = {
            0: "unknown",
            1: "accident",
            2: "fog",
            3: "dangerous_conditions",
            4: "rain",
            5: "ice",
            6: "traffic_jam",
            7: "lane_closed",
            8: "road_closed",
            9: "road_works",
            10: "wind",
            11: "flooding",
            14: "broken_down_vehicle"
        }
        incident_type = incident_type_map.get(icon_category, "other")
        
        # Map magnitude of delay to severity
        magnitude = props.get("magnitudeOfDelay", 0)
        severity_map = {0: "unknown", 1: "minor", 2: "moderate", 3: "major", 4: "undefined"}
        severity = severity_map.get(magnitude, "unknown")
        
        # Extract event descriptions
        events = props.get("events", [])
        descriptions = [event.get("description", "") for event in events if event.get("description")]
        description = "; ".join(descriptions) if descriptions else "Traffic incident"
        
        # Get location - use first coordinate if available
        coordinates = geometry.get("coordinates", [])
        if coordinates and len(coordinates) > 0:
            if isinstance(coordinates[0], list):
                # LineString or MultiPoint
                first_coord = coordinates[0]
            else:
                # Point
                first_coord = coordinates
            location_lon, location_lat = first_coord[0], first_coord[1]
        else:
            location_lon, location_lat = None, None
        
        entity = {
            "id": entity_id,
            "type": "TrafficEvent",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Transportation/master/context.jsonld"
            ],
            "eventType": {
                "type": "Property",
                "value": incident_type
            },
            "severity": {
                "type": "Property",
                "value": severity
            },
            "description": {
                "type": "Property",
                "value": description
            },
            "dateObserved": {
                "type": "Property",
                "value": {
                    "@type": "DateTime",
                    "@value": datetime.utcnow().isoformat() + "Z"
                }
            },
            "source": {
                "type": "Property",
                "value": "TomTom Traffic Incidents API"
            }
        }
        
        # Add location if available
        if location_lon and location_lat:
            entity["location"] = {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [location_lon, location_lat]
                }
            }
        
        # Add affected road segments
        if props.get("from"):
            entity["affectedRoadSegment"] = {
                "type": "Property",
                "value": {
                    "from": props.get("from"),
                    "to": props.get("to")
                }
            }
        
        # Add road numbers
        if props.get("roadNumbers"):
            entity["roadNumbers"] = {
                "type": "Property",
                "value": props["roadNumbers"]
            }
        
        # Add delay information
        if props.get("delay"):
            entity["delay"] = {
                "type": "Property",
                "value": props["delay"],
                "unitCode": "SEC"
            }
        
        # Add length of affected road
        if props.get("length"):
            entity["length"] = {
                "type": "Property",
                "value": props["length"],
                "unitCode": "MTR"
            }
        
        # Add time validity
        if props.get("startTime"):
            entity["startTime"] = {
                "type": "Property",
                "value": {
                    "@type": "DateTime",
                    "@value": props["startTime"]
                }
            }
        
        if props.get("endTime"):
            entity["endTime"] = {
                "type": "Property",
                "value": {
                    "@type": "DateTime",
                    "@value": props["endTime"]
                }
            }
        
        return entity
