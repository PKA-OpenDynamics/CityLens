"""
Import OSM Administrative Boundaries and Facilities to PostgreSQL/PostGIS

This script:
1. Reads OSM PBF file (Vietnam or Hanoi extract)
2. Extracts administrative boundaries (admin_level 4, 6, 8)
3. Extracts facilities (amenities like hospitals, schools, etc.)
4. Inserts data into PostgreSQL with proper PostGIS geometry

Requirements:
- osmium library: pip install osmium
- psycopg2: pip install psycopg2-binary
- shapely: pip install shapely

Usage:
    python scripts/import_osm_admin_structure.py data/osm/vietnam-latest.osm.pbf
    python scripts/import_osm_admin_structure.py data/osm/hanoi.osm.pbf
"""

import osmium
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import execute_values
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, mapping
from shapely.wkt import dumps as wkt_dumps

# Database configuration
# Use citylens_db hostname when running in Docker, localhost for local
import os
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "citylens_db"),
    "port": 5432,
    "database": os.getenv("POSTGRES_DB", "citylens_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres")
}

# Hanoi bounding box for filtering
HANOI_BBOX = {
    "min_lat": 20.53,
    "max_lat": 21.38,
    "min_lon": 105.29,
    "max_lon": 106.02
}

# Facility categories mapping
FACILITY_CATEGORIES = {
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

# Reverse mapping: amenity -> category
AMENITY_TO_CATEGORY = {}
for category, amenities in FACILITY_CATEGORIES.items():
    for amenity in amenities:
        if amenity not in AMENITY_TO_CATEGORY:
            AMENITY_TO_CATEGORY[amenity] = category


class OSMHandler(osmium.SimpleHandler):
    """Handler to extract administrative boundaries and facilities from OSM"""
    
    def __init__(self):
        super(OSMHandler, self).__init__()
        self.admin_areas = []
        self.facilities = []
        self.nodes_cache = {}  # Cache for way geometry
        
    def is_in_hanoi(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within Hanoi bounding box"""
        return (HANOI_BBOX["min_lat"] <= lat <= HANOI_BBOX["max_lat"] and
                HANOI_BBOX["min_lon"] <= lon <= HANOI_BBOX["max_lon"])
    
    def node(self, n):
        """Process nodes (points)"""
        # Cache node for way processing
        if n.location.valid():
            self.nodes_cache[n.id] = (n.location.lon, n.location.lat)
        
        # Check if it's a facility
        if not n.tags:
            return
        
        amenity = n.tags.get("amenity")
        if not amenity or amenity not in AMENITY_TO_CATEGORY:
            return
        
        if not n.location.valid():
            return
        
        lat, lon = n.location.lat, n.location.lon
        
        if not self.is_in_hanoi(lat, lon):
            return
        
        # Extract facility data
        category = AMENITY_TO_CATEGORY[amenity]
        facility = {
            "osm_id": n.id,
            "osm_type": "node",
            "category": category,
            "amenity": amenity,
            "name": n.tags.get("name", "Unnamed"),
            "name_en": n.tags.get("name:en"),
            "name_vi": n.tags.get("name:vi") or n.tags.get("name"),
            "address_street": n.tags.get("addr:street"),
            "address_district": n.tags.get("addr:district"),
            "address_city": n.tags.get("addr:city"),
            "phone": n.tags.get("phone") or n.tags.get("contact:phone"),
            "website": n.tags.get("website"),
            "opening_hours": n.tags.get("opening_hours"),
            "tags": dict(n.tags),
            "location": Point(lon, lat)
        }
        
        self.facilities.append(facility)
    
    def way(self, w):
        """Process ways (lines/areas)"""
        if not w.tags:
            return
        
        # Check for facilities
        amenity = w.tags.get("amenity")
        if amenity and amenity in AMENITY_TO_CATEGORY:
            # Get way geometry
            try:
                coords = [(self.nodes_cache[n.ref][0], self.nodes_cache[n.ref][1]) 
                          for n in w.nodes if n.ref in self.nodes_cache]
                
                if not coords:
                    return
                
                # Calculate center point
                avg_lon = sum(c[0] for c in coords) / len(coords)
                avg_lat = sum(c[1] for c in coords) / len(coords)
                
                if not self.is_in_hanoi(avg_lat, avg_lon):
                    return
                
                category = AMENITY_TO_CATEGORY[amenity]
                facility = {
                    "osm_id": w.id,
                    "osm_type": "way",
                    "category": category,
                    "amenity": amenity,
                    "name": w.tags.get("name", "Unnamed"),
                    "name_en": w.tags.get("name:en"),
                    "name_vi": w.tags.get("name:vi") or w.tags.get("name"),
                    "address_street": w.tags.get("addr:street"),
                    "address_district": w.tags.get("addr:district"),
                    "address_city": w.tags.get("addr:city"),
                    "phone": w.tags.get("phone") or w.tags.get("contact:phone"),
                    "website": w.tags.get("website"),
                    "opening_hours": w.tags.get("opening_hours"),
                    "tags": dict(w.tags),
                    "location": Point(avg_lon, avg_lat)
                }
                
                self.facilities.append(facility)
            except Exception as e:
                print(f"Error processing way {w.id}: {e}")
    
    def relation(self, r):
        """Process relations (complex geometries, admin boundaries)"""
        if not r.tags:
            return
        
        # Check for administrative boundaries
        if r.tags.get("boundary") == "administrative":
            admin_level = r.tags.get("admin_level")
            
            # Only interested in levels 4 (city), 6 (district), 8 (ward)
            if admin_level not in ["4", "6", "8"]:
                return
            
            name = r.tags.get("name", "Unknown")
            
            # Filter by name (must contain Vietnamese keywords or be in Hanoi area)
            if admin_level == "4" and "Hà Nội" not in name:
                return
            
            # Try to get a representative point (simplified - just use first member's location)
            center_lat, center_lon = None, None
            for member in r.members:
                if member.type == 'n' and member.ref in self.nodes_cache:
                    center_lon, center_lat = self.nodes_cache[member.ref]
                    break
            
            # If no center found, skip
            if not center_lat or not center_lon:
                # For Hanoi city, use known center
                if admin_level == "4":
                    center_lat, center_lon = 21.0283334, 105.8540410
                else:
                    return
            
            if admin_level != "4" and not self.is_in_hanoi(center_lat, center_lon):
                return
            
            admin_area = {
                "osm_id": r.id,
                "osm_type": "relation",
                "admin_level": int(admin_level),
                "name": name,
                "name_en": r.tags.get("name:en", ""),
                "name_vi": r.tags.get("name:vi", "") or name,
                "boundary_type": "administrative",
                "population": int(r.tags.get("population", "0")) if r.tags.get("population", "") else None,
                "tags": dict(r.tags),
                "center_point": Point(center_lon, center_lat)
            }
            
            self.admin_areas.append(admin_area)


def insert_admin_areas(conn, admin_areas: List[Dict]):
    """Insert administrative areas into database"""
    if not admin_areas:
        print("No administrative areas to insert")
        return
    
    cursor = conn.cursor()
    
    # Prepare data for batch insert
    values = []
    for area in admin_areas:
        center_wkt = wkt_dumps(area["center_point"])
        
        values.append((
            area["osm_id"],
            area["osm_type"],
            area["admin_level"],
            area["name"],
            area.get("name_en"),
            area.get("name_vi"),
            area.get("boundary_type"),
            area.get("population"),
            json.dumps(area.get("tags", {})),
            f"SRID=4326;{center_wkt}"
        ))
    
    # Batch insert with ON CONFLICT
    insert_query = """
        INSERT INTO administrative_areas 
        (osm_id, osm_type, admin_level, name, name_en, name_vi, boundary_type, 
         population, tags, center_point)
        VALUES %s
        ON CONFLICT (osm_id) DO UPDATE SET
            name = EXCLUDED.name,
            name_en = EXCLUDED.name_en,
            name_vi = EXCLUDED.name_vi,
            population = EXCLUDED.population,
            tags = EXCLUDED.tags,
            center_point = EXCLUDED.center_point,
            updated_at = NOW()
    """
    
    execute_values(cursor, insert_query, values)
    conn.commit()
    
    print(f"✓ Inserted {len(admin_areas)} administrative areas")


def insert_facilities(conn, facilities: List[Dict]):
    """Insert facilities into database"""
    if not facilities:
        print("No facilities to insert")
        return
    
    cursor = conn.cursor()
    
    # Prepare data for batch insert
    values = []
    for facility in facilities:
        location_wkt = wkt_dumps(facility["location"])
        
        values.append((
            facility["osm_id"],
            facility["osm_type"],
            facility["category"],
            facility["amenity"],
            facility["name"],
            facility.get("name_en"),
            facility.get("name_vi"),
            facility.get("address_street"),
            facility.get("address_district"),
            facility.get("address_city"),
            facility.get("phone"),
            facility.get("website"),
            facility.get("opening_hours"),
            json.dumps(facility.get("tags", {})),
            f"SRID=4326;{location_wkt}"
        ))
    
    # Batch insert with ON CONFLICT
    insert_query = """
        INSERT INTO facilities 
        (osm_id, osm_type, category, amenity, name, name_en, name_vi,
         address_street, address_district, address_city, phone, website,
         opening_hours, tags, location)
        VALUES %s
        ON CONFLICT (osm_type, osm_id, amenity) DO UPDATE SET
            name = EXCLUDED.name,
            name_en = EXCLUDED.name_en,
            name_vi = EXCLUDED.name_vi,
            address_street = EXCLUDED.address_street,
            phone = EXCLUDED.phone,
            website = EXCLUDED.website,
            opening_hours = EXCLUDED.opening_hours,
            tags = EXCLUDED.tags,
            location = EXCLUDED.location,
            updated_at = NOW()
    """
    
    execute_values(cursor, insert_query, values)
    conn.commit()
    
    print(f"✓ Inserted {len(facilities)} facilities")


def main():
    if len(sys.argv) < 2:
        print("Usage: python import_osm_admin_structure.py <osm_pbf_file>")
        print("Example: python import_osm_admin_structure.py data/osm/vietnam-latest.osm.pbf")
        sys.exit(1)
    
    pbf_file = sys.argv[1]
    
    if not os.path.exists(pbf_file):
        print(f"Error: File not found: {pbf_file}")
        sys.exit(1)
    
    print(f"🔄 Processing OSM file: {pbf_file}")
    print(f"📍 Filtering for Hanoi bbox: {HANOI_BBOX}")
    
    # Parse OSM file
    handler = OSMHandler()
    handler.apply_file(pbf_file)
    
    print(f"\n📊 Extraction Summary:")
    print(f"  - Administrative areas: {len(handler.admin_areas)}")
    print(f"  - Facilities: {len(handler.facilities)}")
    
    # Breakdown by admin level
    for level in [4, 6, 8]:
        count = len([a for a in handler.admin_areas if a["admin_level"] == level])
        level_name = {4: "City", 6: "Districts", 8: "Wards"}[level]
        print(f"    - Admin level {level} ({level_name}): {count}")
    
    # Breakdown by facility category
    print(f"\n  Facilities by category:")
    for category in set(f["category"] for f in handler.facilities):
        count = len([f for f in handler.facilities if f["category"] == category])
        print(f"    - {category}: {count}")
    
    # Connect to database
    print(f"\n🔄 Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Insert data
    print(f"\n🔄 Inserting into database...")
    insert_admin_areas(conn, handler.admin_areas)
    insert_facilities(conn, handler.facilities)
    
    conn.close()
    
    print(f"\n✅ Import completed successfully!")


if __name__ == "__main__":
    main()
