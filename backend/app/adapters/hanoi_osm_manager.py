# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
OSM Local Data Adapter - Complete Administrative Structure for Hanoi
Fetches and organizes administrative boundaries and facilities by district/ward

Administrative Levels in Vietnam:
- Level 4: Province/City (Thành phố) - Hà Nội
- Level 6: District/County (Quận/Huyện) - 12 quận nội thành + 18 huyện
- Level 8: Ward/Commune (Phường/Xã) - ~580 phường/xã

Facilities categories:
- Healthcare: hospitals, clinics, pharmacies
- Education: schools, universities, kindergartens
- Parks & Recreation: parks, playgrounds, sports centers
- Public Services: police stations, fire stations, post offices
- Transportation: bus stops, parking
"""
import httpx
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import json


class HanoiOSMManager:
    """
    Complete OSM data manager for Hanoi administrative structure.
    Hierarchical organization: City → Districts → Wards → Facilities
    """
    
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    
    # Hanoi extended bounding box (covers all districts including suburban areas)
    HANOI_BBOX = {
        "south": 20.53,  # Extended south to cover Ba Vì, Thường Tín
        "west": 105.29,   # Extended west to cover Sơn Tây
        "north": 21.38,   # Extended north to cover Sóc Sơn
        "east": 106.02    # Extended east to cover Gia Lâm
    }
    
    # Hanoi city relation ID in OSM (found via Nominatim)
    HANOI_RELATION_ID = 1903516  # Thành phố Hà Nội
    
    def __init__(self):
        self.timeout = 300.0  # Complex queries need more time
        self.districts_cache = {}
        self.wards_cache = {}
    
    def _bbox_str(self) -> str:
        """Build bbox string for Overpass query"""
        return f"{self.HANOI_BBOX['south']},{self.HANOI_BBOX['west']},{self.HANOI_BBOX['north']},{self.HANOI_BBOX['east']}"
    
    async def fetch_hanoi_boundary(self) -> Dict[str, Any]:
        """
        Fetch Hanoi city boundary (admin_level=4).
        Use only tags, no geometry to avoid timeout.
        """
        query = f"""
        [out:json][timeout:25];
        relation({self.HANOI_RELATION_ID});
        out tags;
        """
        
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
        
        if not data.get("elements"):
            raise ValueError("Hanoi boundary not found")
        
        element = data["elements"][0]
        tags = element.get("tags", {})
        
        # Create entity with Hanoi center point (from Nominatim)
        entity_id = f"urn:ngsi-ld:AdministrativeArea:Hanoi:City:{self.HANOI_RELATION_ID}"
        
        lat = 21.0283334
        lon = 105.8540410
        
        entity = {
            "id": entity_id,
            "type": "AdministrativeArea",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Administrative/master/context.jsonld"
            ],
            "name": {
                "type": "Property",
                "value": tags.get("name:en", "Hanoi")
            },
            "alternateName": {
                "type": "Property",
                "value": tags.get("name", "Hà Nội")
            },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            },
            "administrativeLevel": {
                "type": "Property",
                "value": "City"
            },
            "adminLevel": {
                "type": "Property",
                "value": 4
            },
            "source": {
                "type": "Property",
                "value": "OpenStreetMap"
            },
            "osmId": {
                "type": "Property",
                "value": f"relation/{self.HANOI_RELATION_ID}"
            }
        }
        
        # Add population if available
        if tags.get("population"):
            entity["population"] = {
                "type": "Property",
                "value": int(tags["population"])
            }
        
        return entity
    
    async def fetch_districts(self) -> List[Dict[str, Any]]:
        """
        Fetch all districts (Quận) and counties (Huyện) in Hanoi.
        Admin level 6 - approximately 30 districts.
        Use simplified query without geometry first, then fetch details.
        """
        # First get list of district IDs without geometry (fast)
        query = f"""
        [out:json][timeout:60];
        (
          relation["boundary"="administrative"]["admin_level"="6"](area:{3600000000 + self.HANOI_RELATION_ID});
        );
        out tags;
        """
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            try:
                # For districts, we'll use a simplified approach - just get center point
                # instead of full geometry to avoid timeout
                tags = element.get("tags", {})
                name_vi = tags.get("name", "Unknown")
                name_en = tags.get("name:en", name_vi)
                osm_id = element["id"]
                
                entity_id = f"urn:ngsi-ld:AdministrativeArea:Hanoi:District:{osm_id}"
                
                # Create simplified entity without geometry for now
                entity = {
                    "id": entity_id,
                    "type": "AdministrativeArea",
                    "@context": [
                        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                        "https://raw.githubusercontent.com/smart-data-models/dataModel.Administrative/master/context.jsonld"
                    ],
                    "name": {
                        "type": "Property",
                        "value": name_en
                    },
                    "alternateName": {
                        "type": "Property",
                        "value": name_vi
                    },
                    "administrativeLevel": {
                        "type": "Property",
                        "value": "District"
                    },
                    "adminLevel": {
                        "type": "Property",
                        "value": 6
                    },
                    "source": {
                        "type": "Property",
                        "value": "OpenStreetMap"
                    },
                    "osmId": {
                        "type": "Property",
                        "value": f"relation/{osm_id}"
                    }
                }
                
                # Add population if available
                if tags.get("population"):
                    entity["population"] = {
                        "type": "Property",
                        "value": int(tags["population"])
                    }
                
                entities.append(entity)
                self.districts_cache[osm_id] = entity
                
            except Exception as e:
                print(f"Error processing district {element.get('id')}: {e}")
                continue
        
        return entities
    
    async def fetch_wards_by_district(self, district_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all wards (Phường/Xã) in a specific district.
        Admin level 8 - approximately 10-30 wards per district.
        """
        query = f"""
        [out:json][timeout:120];
        (
          relation["boundary"="administrative"]["admin_level"="8"](area:{3600000000 + district_id});
        );
        out geom;
        """
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            try:
                entity = self._convert_admin_boundary(element, "Ward", "AdministrativeArea")
                # Add parent district reference
                entity["refDistrict"] = {
                    "type": "Relationship",
                    "object": f"urn:ngsi-ld:AdministrativeArea:Hanoi:District:{district_id}"
                }
                entities.append(entity)
                self.wards_cache[element["id"]] = entity
            except Exception as e:
                print(f"Error processing ward {element.get('id')}: {e}")
                continue
        
        return entities
    
    async def fetch_all_wards(self) -> List[Dict[str, Any]]:
        """
        Fetch ALL wards in Hanoi at once.
        Use simplified query without geometry to avoid timeout.
        """
        query = f"""
        [out:json][timeout:90];
        (
          relation["boundary"="administrative"]["admin_level"="8"](area:{3600000000 + self.HANOI_RELATION_ID});
        );
        out tags;
        """
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            try:
                tags = element.get("tags", {})
                name_vi = tags.get("name", "Unknown")
                name_en = tags.get("name:en", name_vi)
                osm_id = element["id"]
                
                entity_id = f"urn:ngsi-ld:AdministrativeArea:Hanoi:Ward:{osm_id}"
                
                # Create simplified entity without geometry
                entity = {
                    "id": entity_id,
                    "type": "AdministrativeArea",
                    "@context": [
                        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                        "https://raw.githubusercontent.com/smart-data-models/dataModel.Administrative/master/context.jsonld"
                    ],
                    "name": {
                        "type": "Property",
                        "value": name_en
                    },
                    "alternateName": {
                        "type": "Property",
                        "value": name_vi
                    },
                    "administrativeLevel": {
                        "type": "Property",
                        "value": "Ward"
                    },
                    "adminLevel": {
                        "type": "Property",
                        "value": 8
                    },
                    "source": {
                        "type": "Property",
                        "value": "OpenStreetMap"
                    },
                    "osmId": {
                        "type": "Property",
                        "value": f"relation/{osm_id}"
                    }
                }
                
                # Add population if available
                if tags.get("population"):
                    entity["population"] = {
                        "type": "Property",
                        "value": int(tags["population"])
                    }
                
                entities.append(entity)
                self.wards_cache[osm_id] = entity
                
            except Exception as e:
                continue
        
        return entities
    
    async def fetch_facilities_in_area(
        self,
        bbox: Optional[Dict[str, float]] = None,
        categories: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all facilities in an area, organized by category.
        
        Args:
            bbox: Custom bounding box, defaults to Hanoi
            categories: List of facility categories to fetch, defaults to all
        
        Returns:
            Dict with category keys and lists of NGSI-LD entities
        """
        bbox_str = self._bbox_str() if not bbox else f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
        
        facility_types = {
            "healthcare": ["hospital", "clinic", "doctors", "pharmacy", "dentist"],
            "education": ["school", "university", "college", "kindergarten", "library"],
            "parks": ["park"],
            "sports": ["sports_centre", "stadium", "swimming_pool", "pitch"],
            "culture": ["theatre", "museum", "arts_centre", "cinema"],
            "public_services": ["police", "fire_station", "post_office", "townhall", "community_centre"],
            "transportation": ["bus_station", "ferry_terminal", "taxi"],
            "emergency": ["hospital", "police", "fire_station"],
            "worship": ["place_of_worship"],
            "food": ["restaurant", "cafe", "fast_food", "food_court"],
            "shopping": ["marketplace", "supermarket", "mall"]
        }
        
        if categories:
            facility_types = {k: v for k, v in facility_types.items() if k in categories}
        
        results = {}
        
        for category, amenities in facility_types.items():
            try:
                entities = await self._fetch_pois_by_amenity(amenities, bbox_str, category)
                results[category] = entities
                # Rate limiting
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error fetching {category}: {e}")
                results[category] = []
        
        return results
    
    async def _fetch_pois_by_amenity(
        self,
        amenities: List[str],
        bbox_str: str,
        category: str
    ) -> List[Dict[str, Any]]:
        """Fetch POIs for specific amenity types"""
        amenity_filter = "|".join(amenities)
        
        query = f"""
        [out:json][timeout:90];
        (
          node["amenity"~"^({amenity_filter})$"]({bbox_str});
          way["amenity"~"^({amenity_filter})$"]({bbox_str});
          relation["amenity"~"^({amenity_filter})$"]({bbox_str});
        );
        out center tags;
        """
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.OVERPASS_URL,
                data={"data": query}
            )
            response.raise_for_status()
            data = response.json()
        
        entities = []
        for element in data.get("elements", []):
            try:
                entity = self._convert_poi(element, category)
                if entity:
                    entities.append(entity)
            except Exception:
                continue
        
        return entities
    
    def _convert_admin_boundary(
        self,
        element: Dict[str, Any],
        level_name: str,
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Convert OSM administrative boundary to NGSI-LD entity.
        """
        tags = element.get("tags", {})
        osm_id = element["id"]
        
        # Get names in multiple languages
        name_vi = tags.get("name", "Unknown")
        name_en = tags.get("name:en", name_vi)
        
        # Extract geometry
        geometry = self._extract_geometry(element)
        
        entity_id = f"urn:ngsi-ld:{entity_type}:Hanoi:{level_name}:{osm_id}"
        
        entity = {
            "id": entity_id,
            "type": entity_type,
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Administrative/master/context.jsonld"
            ],
            "name": {
                "type": "Property",
                "value": name_en
            },
            "alternateName": {
                "type": "Property",
                "value": name_vi
            },
            "location": {
                "type": "GeoProperty",
                "value": geometry
            },
            "administrativeLevel": {
                "type": "Property",
                "value": level_name
            },
            "adminLevel": {
                "type": "Property",
                "value": int(tags.get("admin_level", 8))
            },
            "source": {
                "type": "Property",
                "value": "OpenStreetMap"
            },
            "osmId": {
                "type": "Property",
                "value": f"relation/{osm_id}"
            }
        }
        
        # Add population if available
        if tags.get("population"):
            entity["population"] = {
                "type": "Property",
                "value": int(tags["population"])
            }
        
        # Add area if calculable
        if geometry["type"] in ["Polygon", "MultiPolygon"]:
            try:
                geom = shape(geometry)
                # Approximate area in km²
                area_km2 = geom.area * 111 * 111  # Rough conversion for lat/lon
                entity["area"] = {
                    "type": "Property",
                    "value": round(area_km2, 2),
                    "unitCode": "KMK"  # Square kilometers
                }
            except:
                pass
        
        return entity
    
    def _convert_poi(self, element: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """Convert OSM POI to NGSI-LD PointOfInterest"""
        tags = element.get("tags", {})
        
        # Get coordinates
        if element["type"] == "node":
            lon, lat = element.get("lon"), element.get("lat")
        elif "center" in element:
            lon, lat = element["center"].get("lon"), element["center"].get("lat")
        else:
            return None
        
        if not lon or not lat:
            return None
        
        name = tags.get("name:en") or tags.get("name", "Unnamed")
        amenity = tags.get("amenity", category)
        
        entity_id = f"urn:ngsi-ld:PointOfInterest:Hanoi:{category}:{element['type']}:{element['id']}"
        
        entity = {
            "id": entity_id,
            "type": "PointOfInterest",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.PointOfInterest/master/context.jsonld"
            ],
            "name": {
                "type": "Property",
                "value": name
            },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            },
            "category": {
                "type": "Property",
                "value": [category, amenity]
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
        
        # Add address if available
        address_parts = []
        if tags.get("addr:street"):
            address_parts.append(tags["addr:street"])
        if tags.get("addr:district"):
            address_parts.append(tags["addr:district"])
        
        if address_parts:
            entity["address"] = {
                "type": "Property",
                "value": {
                    "streetAddress": ", ".join(address_parts),
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                }
            }
        
        # Add phone if available
        if tags.get("phone") or tags.get("contact:phone"):
            entity["contactPoint"] = {
                "type": "Property",
                "value": {
                    "telephone": tags.get("phone") or tags.get("contact:phone")
                }
            }
        
        # Add website
        if tags.get("website"):
            entity["url"] = {
                "type": "Property",
                "value": tags["website"]
            }
        
        # Add opening hours
        if tags.get("opening_hours"):
            entity["openingHours"] = {
                "type": "Property",
                "value": tags["opening_hours"]
            }
        
        return entity
    
    def _extract_geometry(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GeoJSON geometry from OSM element"""
        if element["type"] == "node":
            return {
                "type": "Point",
                "coordinates": [element["lon"], element["lat"]]
            }
        
        elif element["type"] == "way":
            if "geometry" in element:
                coords = [[pt["lon"], pt["lat"]] for pt in element["geometry"]]
                # Check if it's a closed way (polygon)
                if coords[0] == coords[-1]:
                    return {
                        "type": "Polygon",
                        "coordinates": [coords]
                    }
                else:
                    return {
                        "type": "LineString",
                        "coordinates": coords
                    }
        
        elif element["type"] == "relation":
            # For relations, try to extract outer boundaries
            if "members" in element:
                outer_coords = []
                for member in element["members"]:
                    if member.get("role") == "outer" and "geometry" in member:
                        coords = [[pt["lon"], pt["lat"]] for pt in member["geometry"]]
                        outer_coords.append(coords)
                
                if outer_coords:
                    if len(outer_coords) == 1:
                        return {
                            "type": "Polygon",
                            "coordinates": outer_coords
                        }
                    else:
                        return {
                            "type": "MultiPolygon",
                            "coordinates": [outer_coords]
                        }
        
        # Fallback: return a point from center if available
        if "center" in element:
            return {
                "type": "Point",
                "coordinates": [element["center"]["lon"], element["center"]["lat"]]
            }
        
        raise ValueError(f"Cannot extract geometry from element {element.get('id')}")
