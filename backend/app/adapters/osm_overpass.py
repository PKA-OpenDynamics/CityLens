import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

class OSMOverpassAdapter:
    """
    Adapter to fetch real data from OpenStreetMap using Overpass API
    for Hanoi city and convert to NGSI-LD format.
    """
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    # Hanoi bounding box (approximate)
    HANOI_BBOX = {
        "south": 20.8,
        "west": 105.6,
        "north": 21.2,
        "east": 106.0
    }
    
    def __init__(self):
        self.timeout = 60.0  # OSM queries can take time
    
    def _build_bbox_query(self) -> str:
        """Build bbox string for Overpass query"""
        return f"{self.HANOI_BBOX['south']},{self.HANOI_BBOX['west']},{self.HANOI_BBOX['north']},{self.HANOI_BBOX['east']}"
    
    async def fetch_administrative_boundaries(self) -> List[Dict[str, Any]]:
        """
        Fetch Hanoi administrative boundaries (districts, wards).
        Returns NGSI-LD entities.
        """
        query = f"""
        [out:json][timeout:60];
        (
          relation["boundary"="administrative"]["admin_level"~"^(5|6|7|8)$"]["name:en"~"Hanoi|Ha Noi",i]({self._build_bbox_query()});
          way["boundary"="administrative"]["admin_level"~"^(5|6|7|8)$"]({self._build_bbox_query()});
        );
        out geom;
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            if element.get("type") not in ["way", "relation"]:
                continue
            
            tags = element.get("tags", {})
            name = tags.get("name:en") or tags.get("name", "Unknown")
            admin_level = tags.get("admin_level", "8")
            
            # Extract geometry
            geometry = self._extract_geometry(element)
            if not geometry:
                continue
            
            entity_id = f"urn:ngsi-ld:AdministrativeArea:Hanoi:{element['type']}:{element['id']}"
            
            entity = {
                "id": entity_id,
                "type": "AdministrativeArea",
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ],
                "location": {
                    "type": "GeoProperty",
                    "value": geometry
                },
                "name": {
                    "type": "Property",
                    "value": name
                },
                "adminLevel": {
                    "type": "Property",
                    "value": int(admin_level)
                },
                "source": {
                    "type": "Property",
                    "value": "OpenStreetMap"
                },
                "osmId": {
                    "type": "Property",
                    "value": f"{element['type']}/{element['id']}"
                }
            }
            
            entities.append(entity)
        
        return entities
    
    async def fetch_pois(self, poi_type: str, amenity_tags: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch Points of Interest (hospitals, schools, parks, etc.)
        
        Args:
            poi_type: NGSI-LD type (e.g., "PointOfInterest", "Hospital", "School")
            amenity_tags: OSM amenity tags to search for
        """
        amenity_filter = "|".join(amenity_tags)
        query = f"""
        [out:json][timeout:60];
        (
          node["amenity"~"{amenity_filter}"]({self._build_bbox_query()});
          way["amenity"~"{amenity_filter}"]({self._build_bbox_query()});
        );
        out center;
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name:en") or tags.get("name", "Unnamed")
            
            # Get coordinates
            if element["type"] == "node":
                lon, lat = element["lon"], element["lat"]
            elif "center" in element:
                lon, lat = element["center"]["lon"], element["center"]["lat"]
            else:
                continue
            
            entity_id = f"urn:ngsi-ld:{poi_type}:Hanoi:{element['type']}:{element['id']}"
            
            entity = {
                "id": entity_id,
                "type": poi_type,
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ],
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                },
                "name": {
                    "type": "Property",
                    "value": name
                },
                "category": {
                    "type": "Property",
                    "value": tags.get("amenity", "unknown")
                },
                "address": {
                    "type": "Property",
                    "value": {
                        "streetAddress": tags.get("addr:street", ""),
                        "addressLocality": tags.get("addr:city", "Hanoi"),
                        "addressCountry": "VN"
                    }
                },
                "source": {
                    "type": "Property",
                    "value": "OpenStreetMap"
                },
                "osmId": {
                    "type": "Property",
                    "value": f"{element['type']}/{element['id']}"
                }
            }
            
            # Add specific attributes based on amenity type
            if tags.get("phone"):
                entity["telephone"] = {
                    "type": "Property",
                    "value": tags["phone"]
                }
            
            if tags.get("website"):
                entity["url"] = {
                    "type": "Property",
                    "value": tags["website"]
                }
            
            if tags.get("opening_hours"):
                entity["openingHours"] = {
                    "type": "Property",
                    "value": tags["opening_hours"]
                }
            
            entities.append(entity)
        
        return entities
    
    async def fetch_parking_spots(self) -> List[Dict[str, Any]]:
        """Fetch parking areas in Hanoi"""
        query = f"""
        [out:json][timeout:60];
        (
          node["amenity"="parking"]({self._build_bbox_query()});
          way["amenity"="parking"]({self._build_bbox_query()});
        );
        out center;
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name:en") or tags.get("name", "Parking Area")
            
            if element["type"] == "node":
                lon, lat = element["lon"], element["lat"]
            elif "center" in element:
                lon, lat = element["center"]["lon"], element["center"]["lat"]
            else:
                continue
            
            entity_id = f"urn:ngsi-ld:OffStreetParking:Hanoi:{element['type']}:{element['id']}"
            
            entity = {
                "id": entity_id,
                "type": "OffStreetParking",
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"
                ],
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                },
                "name": {
                    "type": "Property",
                    "value": name
                },
                "category": {
                    "type": "Property",
                    "value": [tags.get("parking", "surface")]
                },
                "address": {
                    "type": "Property",
                    "value": {
                        "addressLocality": "Hanoi",
                        "addressCountry": "VN"
                    }
                },
                "source": {
                    "type": "Property",
                    "value": "OpenStreetMap"
                }
            }
            
            # Add capacity if available
            if tags.get("capacity"):
                try:
                    entity["totalSpotNumber"] = {
                        "type": "Property",
                        "value": int(tags["capacity"])
                    }
                except ValueError:
                    pass
            
            entities.append(entity)
        
        return entities
    
    async def fetch_bus_stops(self) -> List[Dict[str, Any]]:
        """Fetch public transport stops in Hanoi"""
        query = f"""
        [out:json][timeout:60];
        (
          node["highway"="bus_stop"]({self._build_bbox_query()});
          node["public_transport"="stop_position"]({self._build_bbox_query()});
        );
        out;
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            if element["type"] != "node":
                continue
            
            tags = element.get("tags", {})
            name = tags.get("name:en") or tags.get("name", "Bus Stop")
            
            entity_id = f"urn:ngsi-ld:PublicTransportStop:Hanoi:node:{element['id']}"
            
            entity = {
                "id": entity_id,
                "type": "PublicTransportStop",
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ],
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [element["lon"], element["lat"]]
                    }
                },
                "name": {
                    "type": "Property",
                    "value": name
                },
                "transportationType": {
                    "type": "Property",
                    "value": ["bus"]
                },
                "address": {
                    "type": "Property",
                    "value": {
                        "addressLocality": "Hanoi",
                        "addressCountry": "VN"
                    }
                },
                "source": {
                    "type": "Property",
                    "value": "OpenStreetMap"
                }
            }
            
            entities.append(entity)
        
        return entities
    
    def _extract_geometry(self, element: Dict) -> Optional[Dict]:
        """Extract GeoJSON geometry from OSM element"""
        if element["type"] == "node":
            return {
                "type": "Point",
                "coordinates": [element["lon"], element["lat"]]
            }
        elif element["type"] == "way" and "geometry" in element:
            coords = [[node["lon"], node["lat"]] for node in element["geometry"]]
            if len(coords) > 2:
                # Close the polygon if needed
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                return {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
        elif element["type"] == "relation" and "members" in element:
            # For relations, we'd need to process members
            # For now, return center point if available
            if "center" in element:
                return {
                    "type": "Point",
                    "coordinates": [element["center"]["lon"], element["center"]["lat"]]
                }
        
        return None

