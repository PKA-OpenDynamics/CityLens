"""
OSM Data Downloader and Processor for Hanoi

This module handles downloading OSM data extracts for Hanoi and processing them
into NGSI-LD entities without relying on Overpass API.

Data source: Geofabrik (https://download.geofabrik.de/asia/vietnam.html)
"""

import httpx
import osmium
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

class HanoiOSMDataManager:
    """
    Manages OSM data for Hanoi:
    1. Downloads Vietnam OSM extract from Geofabrik
    2. Filters for Hanoi bounding box
    3. Converts to NGSI-LD entities
    4. Stores in database
    """
    
    # Geofabrik Vietnam extract URL (updated daily)
    VIETNAM_OSM_URL = "https://download.geofabrik.de/asia/vietnam-latest.osm.pbf"
    
    # Hanoi bounding box
    HANOI_BBOX = {
        "min_lat": 20.8,
        "min_lon": 105.6,
        "max_lat": 21.2,
        "max_lon": 106.0
    }
    
    def __init__(self, data_dir: str = "./osm_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.osm_file = self.data_dir / "vietnam-latest.osm.pbf"
        self.hanoi_file = self.data_dir / "hanoi.osm.pbf"
    
    async def download_vietnam_extract(self) -> Path:
        """
        Download Vietnam OSM extract from Geofabrik.
        File size: ~200MB, updated daily.
        """
        print(f"📥 Downloading Vietnam OSM extract...")
        print(f"   Source: {self.VIETNAM_OSM_URL}")
        print(f"   Target: {self.osm_file}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream("GET", self.VIETNAM_OSM_URL) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                
                with open(self.osm_file, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indicator
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}% ({downloaded / 1024 / 1024:.1f}MB)", end="")
        
        print(f"\n✅ Download complete: {self.osm_file}")
        return self.osm_file
    
    def extract_hanoi_data(self) -> Path:
        """
        Extract only Hanoi data from Vietnam file using osmium.
        This reduces file size from ~200MB to ~50MB.
        """
        print(f"✂️  Extracting Hanoi data from Vietnam extract...")
        
        # Use osmium-tool to extract bounding box
        # osmium extract -b 105.6,20.8,106.0,21.2 vietnam-latest.osm.pbf -o hanoi.osm.pbf
        
        import subprocess
        
        bbox_str = f"{self.HANOI_BBOX['min_lon']},{self.HANOI_BBOX['min_lat']},{self.HANOI_BBOX['max_lon']},{self.HANOI_BBOX['max_lat']}"
        
        cmd = [
            "osmium", "extract",
            "-b", bbox_str,
            str(self.osm_file),
            "-o", str(self.hanoi_file),
            "--overwrite"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Hanoi extract created: {self.hanoi_file}")
            return self.hanoi_file
        except subprocess.CalledProcessError as e:
            print(f"⚠️  osmium-tool not found. Using full Vietnam file.")
            return self.osm_file
        except FileNotFoundError:
            print(f"⚠️  osmium-tool not installed. Install with: apt-get install osmium-tool")
            return self.osm_file


class HanoiOSMParser(osmium.SimpleHandler):
    """
    Parse OSM PBF file and extract relevant entities for Hanoi.
    Converts to NGSI-LD format on-the-fly.
    """
    
    def __init__(self, bbox: Dict[str, float]):
        osmium.SimpleHandler.__init__(self)
        self.bbox = bbox
        self.entities = {
            "bus_stops": [],
            "hospitals": [],
            "schools": [],
            "parks": [],
            "parking": [],
            "admin_boundaries": []
        }
    
    def _in_bbox(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Hanoi bbox"""
        return (
            self.bbox["min_lat"] <= lat <= self.bbox["max_lat"] and
            self.bbox["min_lon"] <= lon <= self.bbox["max_lon"]
        )
    
    def node(self, n):
        """Process OSM nodes (points)"""
        if not self._in_bbox(n.location.lat, n.location.lon):
            return
        
        tags = {tag.k: tag.v for tag in n.tags}
        
        # Bus stops
        if tags.get("highway") == "bus_stop" or tags.get("public_transport") == "stop_position":
            self.entities["bus_stops"].append(self._create_bus_stop_entity(n, tags))
        
        # Hospitals
        elif tags.get("amenity") in ["hospital", "clinic", "doctors"]:
            self.entities["hospitals"].append(self._create_poi_entity(n, tags, "Hospital"))
        
        # Schools
        elif tags.get("amenity") in ["school", "university", "college", "kindergarten"]:
            self.entities["schools"].append(self._create_poi_entity(n, tags, "School"))
        
        # Parking
        elif tags.get("amenity") == "parking":
            self.entities["parking"].append(self._create_parking_entity(n, tags))
    
    def way(self, w):
        """Process OSM ways (lines/polygons)"""
        # For ways, we need to check if any node is in bbox
        # For simplicity, check the first node
        if not w.nodes:
            return
        
        try:
            first_node = w.nodes[0]
            if not self._in_bbox(first_node.lat, first_node.lon):
                return
        except:
            return
        
        tags = {tag.k: tag.v for tag in w.tags}
        
        # Parks
        if tags.get("leisure") == "park":
            self.entities["parks"].append(self._create_park_entity(w, tags))
        
        # Parking areas
        elif tags.get("amenity") == "parking":
            self.entities["parking"].append(self._create_parking_entity_from_way(w, tags))
    
    def _create_bus_stop_entity(self, node, tags: Dict) -> Dict[str, Any]:
        """Create NGSI-LD entity for bus stop"""
        name = tags.get("name:en") or tags.get("name", "Bus Stop")
        
        return {
            "id": f"urn:ngsi-ld:PublicTransportStop:Hanoi:node:{node.id}",
            "type": "PublicTransportStop",
            "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [node.location.lon, node.location.lat]
                }
            },
            "name": {"type": "Property", "value": name},
            "transportationType": {"type": "Property", "value": ["bus"]},
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                }
            },
            "source": {"type": "Property", "value": "OpenStreetMap"},
            "osmId": {"type": "Property", "value": f"node/{node.id}"}
        }
    
    def _create_poi_entity(self, node, tags: Dict, poi_type: str) -> Dict[str, Any]:
        """Create NGSI-LD entity for POI"""
        name = tags.get("name:en") or tags.get("name", f"Unnamed {poi_type}")
        
        entity = {
            "id": f"urn:ngsi-ld:PointOfInterest:Hanoi:{poi_type}:{node.id}",
            "type": "PointOfInterest",
            "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [node.location.lon, node.location.lat]
                }
            },
            "name": {"type": "Property", "value": name},
            "category": {"type": "Property", "value": tags.get("amenity", poi_type.lower())},
            "address": {
                "type": "Property",
                "value": {
                    "streetAddress": tags.get("addr:street", ""),
                    "addressLocality": "Hanoi",
                    "addressCountry": "VN"
                }
            },
            "source": {"type": "Property", "value": "OpenStreetMap"}
        }
        
        # Add optional fields
        if tags.get("phone"):
            entity["telephone"] = {"type": "Property", "value": tags["phone"]}
        if tags.get("website"):
            entity["url"] = {"type": "Property", "value": tags["website"]}
        
        return entity
    
    def _create_parking_entity(self, node, tags: Dict) -> Dict[str, Any]:
        """Create NGSI-LD entity for parking"""
        name = tags.get("name:en") or tags.get("name", "Parking Area")
        
        entity = {
            "id": f"urn:ngsi-ld:OffStreetParking:Hanoi:node:{node.id}",
            "type": "OffStreetParking",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "https://raw.githubusercontent.com/smart-data-models/dataModel.Parking/master/context.jsonld"
            ],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [node.location.lon, node.location.lat]
                }
            },
            "name": {"type": "Property", "value": name},
            "category": {"type": "Property", "value": [tags.get("parking", "surface")]},
            "source": {"type": "Property", "value": "OpenStreetMap"}
        }
        
        if tags.get("capacity"):
            try:
                entity["totalSpotNumber"] = {"type": "Property", "value": int(tags["capacity"])}
            except ValueError:
                pass
        
        return entity
    
    def _create_parking_entity_from_way(self, way, tags: Dict) -> Dict[str, Any]:
        """Create parking entity from way (polygon)"""
        # Calculate centroid
        lats = [n.lat for n in way.nodes if n.lat]
        lons = [n.lon for n in way.nodes if n.lon]
        
        if not lats or not lons:
            return None
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        name = tags.get("name:en") or tags.get("name", "Parking Area")
        
        return {
            "id": f"urn:ngsi-ld:OffStreetParking:Hanoi:way:{way.id}",
            "type": "OffStreetParking",
            "@context": [
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [center_lon, center_lat]
                }
            },
            "name": {"type": "Property", "value": name},
            "source": {"type": "Property", "value": "OpenStreetMap"}
        }
    
    def _create_park_entity(self, way, tags: Dict) -> Dict[str, Any]:
        """Create park entity from way"""
        lats = [n.lat for n in way.nodes if n.lat]
        lons = [n.lon for n in way.nodes if n.lon]
        
        if not lats or not lons:
            return None
        
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        
        name = tags.get("name:en") or tags.get("name", "Park")
        
        return {
            "id": f"urn:ngsi-ld:PointOfInterest:Hanoi:Park:{way.id}",
            "type": "PointOfInterest",
            "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [center_lon, center_lat]
                }
            },
            "name": {"type": "Property", "value": name},
            "category": {"type": "Property", "value": "park"},
            "source": {"type": "Property", "value": "OpenStreetMap"}
        }

