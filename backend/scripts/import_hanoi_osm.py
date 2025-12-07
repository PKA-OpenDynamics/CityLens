#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Import dữ liệu Hà Nội từ vietnam-latest.osm.pbf
Chỉ import administrative boundaries, streets, buildings và POIs của Hà Nội
Sử dụng OSM relation ID để lấy boundary chính xác thay vì hardcode bbox
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import osmium
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import WKTElement
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, shape
from shapely.ops import unary_union
from shapely import wkb
import json

from app.core.config import settings
from app.models.geographic import (
    AdministrativeBoundary, 
    Street, 
    Building, 
    POI
)

# Hà Nội OSM relation ID và bbox chính xác từ OSM
HANOI_RELATION_ID = 1903515  # relation/1903515 on OSM
# Bbox from https://www.openstreetmap.org/relation/1903515
HANOI_BBOX = {
    'min_lon': 105.341,
    'min_lat': 20.538,
    'max_lon': 106.020,
    'max_lat': 21.380
}


class HanoiBoundaryExtractor(osmium.SimpleHandler):
    """Pass 1: Extract Hanoi boundary polygon từ relation"""
    
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.hanoi_polygon = None
        self.hanoi_bbox = None
        
    def area(self, a):
        """Process areas (relations converted to polygons)"""
        if a.from_way():
            return
        
        if a.orig_id() == HANOI_RELATION_ID:
            print(f"  🎯 Found Hanoi relation {HANOI_RELATION_ID}")
            
            # Extract geometry
            try:
                # Get all outer rings
                outer_rings = []
                for ring in a.outer_rings():
                    coords = [(node.lon, node.lat) for node in ring]
                    if len(coords) >= 3:
                        outer_rings.append(Polygon(coords))
                
                if outer_rings:
                    # Combine all outer rings
                    self.hanoi_polygon = unary_union(outer_rings)
                    self.hanoi_bbox = self.hanoi_polygon.bounds  # (minx, miny, maxx, maxy)
                    
                    print(f"  ✅ Extracted Hanoi boundary polygon")
                    print(f"     Bbox: {self.hanoi_bbox}")
                    
            except Exception as e:
                print(f"  ⚠️  Error extracting geometry: {e}")


class HanoiOSMHandler(osmium.SimpleHandler):
    """Pass 2: Extract dữ liệu Hà Nội dựa trên boundary polygon"""
    
    def __init__(self, hanoi_polygon=None, hanoi_bbox=None):
        osmium.SimpleHandler.__init__(self)
        self.admin_boundaries = []
        self.streets = []
        self.buildings = []
        self.pois = []
        self.hanoi_polygon = hanoi_polygon
        self.hanoi_bbox = hanoi_bbox  # (minx, miny, maxx, maxy)
        self.processed_count = 0
        
        # Store relation parent-child relationships
        self.hanoi_related_ids = set([HANOI_RELATION_ID])  # Start with Hanoi itself
        
    def _in_hanoi(self, lat, lon):
        """Check if coordinate is within Hanoi boundary"""
        if self.hanoi_bbox:
            # Quick bbox check first
            minx, miny, maxx, maxy = self.hanoi_bbox
            if not (miny <= lat <= maxy and minx <= lon <= maxx):
                return False
        
        # If we have polygon, do precise check
        if self.hanoi_polygon:
            point = Point(lon, lat)
            return self.hanoi_polygon.contains(point)
        
        # Fallback to True if no boundary (will get everything)
        return True
    
    def _get_tags_dict(self, tags):
        """Convert osmium tags to dict"""
        return {tag.k: tag.v for tag in tags}
    
    def _create_point_geometry(self, location):
        """Create WKT point from location"""
        return f"POINT({location.lon} {location.lat})"
    
    def _create_linestring_geometry(self, nodes):
        """Create WKT linestring from node list"""
        coords = [(node.lon, node.lat) for node in nodes if node.location.valid()]
        if len(coords) < 2:
            return None
        return LineString(coords).wkt
    
    def _create_polygon_geometry(self, nodes):
        """Create WKT polygon from node list"""
        coords = [(node.lon, node.lat) for node in nodes if node.location.valid()]
        if len(coords) < 3:
            return None
        # Close the polygon if not closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        try:
            return Polygon(coords).wkt
        except:
            return None
    
    def relation(self, r):
        """Process relations (administrative boundaries) - TWO PASS approach"""
        tags = self._get_tags_dict(r.tags)
        
        # Check if this is an administrative boundary
        if 'boundary' not in tags or tags['boundary'] != 'administrative':
            return
        
        admin_level = tags.get('admin_level')
        if not admin_level:
            return
        
        try:
            admin_level = int(admin_level)
        except:
            return
        
        # Only get admin_level 4-7
        if admin_level < 4 or admin_level > 7:
            return
        
        name = tags.get('name', '').strip()
        name_en = tags.get('name:en', '').strip()
        
        # STRICT FILTER: Only accept if:
        # 1. It's Hanoi city itself (admin_level=4, name="Hà Nội")
        # 2. OR tags explicitly mention Hanoi in name
        
        is_hanoi_related = False
        
        if admin_level == 4:
            # Must be exactly "Hà Nội" or "Hanoi"
            if name in ['Hà Nội', 'Hanoi', 'Thành phố Hà Nội']:
                is_hanoi_related = True
                self.hanoi_related_ids.add(r.id)
        else:
            # For subdivisions (5-7), check if name contains Hanoi reference
            # or if any member tags indicate Hanoi
            name_lower = name.lower()
            
            # Check if it's within Hanoi administrative structure
            # This is done by checking member relations
            for member in r.members:
                if member.type == 'r' and member.ref in self.hanoi_related_ids:
                    is_hanoi_related = True
                    self.hanoi_related_ids.add(r.id)
                    break
            
            # Also check if name/tags explicitly mention Hanoi
            if not is_hanoi_related:
                # Check various name tags for Hanoi references
                for tag_key in ['name', 'name:vi', 'official_name', 'alt_name']:
                    if tag_key in tags:
                        tag_value = tags[tag_key].lower()
                        if 'hà nội' in tag_value or 'hanoi' in tag_value or 'ha noi' in tag_value:
                            is_hanoi_related = True
                            self.hanoi_related_ids.add(r.id)
                            break
        
        if not is_hanoi_related:
            return
        
        print(f"  📍 Found admin boundary: {name} (level {admin_level}, id={r.id})")
        
        self.admin_boundaries.append({
            'osm_id': r.id,
            'osm_type': 'relation',
            'name': name,
            'name_en': name_en if name_en else None,
            'admin_level': admin_level,
            'tags': json.dumps(tags),
            # Geometry will be processed separately using osmium export
        })
        
        self.processed_count += 1
        if self.processed_count % 100 == 0:
            print(f"  Processed {self.processed_count} items...")
    
    def way(self, w):
        """Process ways (streets, buildings)"""
        tags = self._get_tags_dict(w.tags)
        
        # Check if any node is in Hanoi
        if not any(self._in_hanoi(node.lat, node.lon) 
                   for node in w.nodes if node.location.valid()):
            return
        
        # Streets (highways)
        if 'highway' in tags:
            name = tags.get('name', '').strip()
            highway_type = tags['highway']
            
            # Only major roads
            if highway_type in ['motorway', 'trunk', 'primary', 'secondary', 
                               'tertiary', 'residential', 'service']:
                
                geometry_wkt = self._create_linestring_geometry(w.nodes)
                if not geometry_wkt:
                    return
                
                # Parse numeric fields safely
                lanes = None
                if 'lanes' in tags:
                    try:
                        lanes = int(tags['lanes'])
                    except (ValueError, TypeError):
                        pass
                
                maxspeed = None
                if 'maxspeed' in tags:
                    try:
                        maxspeed = int(tags['maxspeed'])
                    except (ValueError, TypeError):
                        pass
                
                self.streets.append({
                    'osm_id': w.id,
                    'osm_type': 'way',
                    'name': name if name else None,
                    'name_en': tags.get('name:en'),
                    'highway_type': highway_type,
                    'surface': tags.get('surface'),
                    'lanes': lanes,
                    'maxspeed': maxspeed,
                    'oneway': tags.get('oneway') == 'yes',
                    'geometry_wkt': geometry_wkt,
                    'tags': json.dumps(tags)
                })
        
        # Buildings
        elif 'building' in tags:
            name = tags.get('name', '').strip()
            building_type = tags.get('building', 'yes')
            
            geometry_wkt = self._create_polygon_geometry(w.nodes)
            if not geometry_wkt:
                return
            
            # Parse building levels safely
            levels = None
            if 'building:levels' in tags:
                try:
                    levels = int(tags['building:levels'])
                except (ValueError, TypeError):
                    pass
            
            self.buildings.append({
                'osm_id': w.id,
                'osm_type': 'way',
                'name': name if name else None,
                'building_type': building_type,
                'addr_street': tags.get('addr:street'),
                'addr_housenumber': tags.get('addr:housenumber'),
                'addr_district': tags.get('addr:district'),
                'levels': levels,
                'geometry_wkt': geometry_wkt,
                'tags': json.dumps(tags)
            })
    
    def node(self, n):
        """Process nodes (POIs)"""
        tags = self._get_tags_dict(n.tags)
        
        # Check if in Hanoi
        if not self._in_hanoi(n.location.lat, n.location.lon):
            return
        
        # POIs (amenity, shop, tourism, etc)
        category = None
        subcategory = None
        
        if 'amenity' in tags:
            category = 'amenity'
            subcategory = tags['amenity']
        elif 'shop' in tags:
            category = 'shop'
            subcategory = tags['shop']
        elif 'tourism' in tags:
            category = 'tourism'
            subcategory = tags['tourism']
        elif 'leisure' in tags:
            category = 'leisure'
            subcategory = tags['leisure']
        else:
            return  # Not a POI
        
        name = tags.get('name', '').strip()
        
        geometry_wkt = self._create_point_geometry(n.location)
        
        self.pois.append({
            'osm_id': n.id,
            'osm_type': 'node',
            'name': name if name else None,
            'name_en': tags.get('name:en'),
            'category': category,
            'subcategory': subcategory,
            'phone': tags.get('phone'),
            'website': tags.get('website'),
            'email': tags.get('email'),
            'opening_hours': tags.get('opening_hours'),
            'geometry_wkt': geometry_wkt,
            'tags': json.dumps(tags)
        })


def print_separator(title=""):
    """Print a formatted separator line"""
    if title:
        print(f"\n{'=' * 80}")
        print(f"{title:^80}")
        print('=' * 80)
    else:
        print('=' * 80)


def print_step(step_num, title):
    """Print step header"""
    print(f"\n{'─' * 80}")
    print(f"STEP {step_num}: {title}")
    print('─' * 80)


def import_hanoi_osm():
    """
    Import Hà Nội data from OSM file
    Uses hanoi-full.osm.pbf extracted with accurate bbox and complete_ways strategy
    """
    import time
    
    hanoi_file = '/app/data/osm/hanoi-full.osm.pbf'
    
    print_separator("🏙️  CITYLENS - HANOI OSM DATA IMPORT")
    
    # Check file exists
    if not os.path.exists(hanoi_file):
        print(f"\n❌ Hanoi OSM file not found: {hanoi_file}")
        print(f"\n📝 To create this file, run inside backend container:")
        print(f"   cd /app/data/osm")
        print(f"   osmium extract --bbox 105.2889615,20.5645154,106.0200725,21.3854176 \\")
        print(f"     --strategy complete_ways vietnam-latest.osm.pbf -o hanoi-full.osm.pbf")
        return False
    
    # File info
    file_size_mb = os.path.getsize(hanoi_file) / (1024 * 1024)
    print(f"\n📁 Source File Information:")
    print(f"   Path: {hanoi_file}")
    print(f"   Size: {file_size_mb:.2f} MB")
    print(f"   Format: OSM PBF (binary)")
    
    print(f"\n📍 Hanoi Geographic Data:")
    print(f"   OSM Relation ID: r{HANOI_RELATION_ID}")
    print(f"   Name: Thành phố Hà Nội")
    print(f"   Accurate Bounding Box: (105.2889615, 20.5645154) to (106.0200725, 21.3854176)")
    print(f"   Approximate Area: ~3,360 km²")
    print(f"   Extraction Strategy: complete_ways (includes all referenced nodes)")
    
    # STEP 1: Parse OSM data
    print_step(1, "PARSING OSM DATA")
    
    handler = HanoiOSMHandler(hanoi_polygon=None, hanoi_bbox=None)
    
    print(f"\nParsing OSM file...")
    start_parse = time.time()
    
    try:
        handler.apply_file(hanoi_file, locations=True)
        parse_duration = time.time() - start_parse
        
        print(f"Parsing completed in {parse_duration:.1f} seconds")
    except Exception as e:
        print(f"\nError parsing OSM file: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\nData Extraction Summary:")
    print(f"   ├─ Administrative boundaries: {len(handler.admin_boundaries):,}")
    print(f"   ├─ Streets: {len(handler.streets):,}")
    print(f"   ├─ Buildings: {len(handler.buildings):,}")
    print(f"   └─ POIs: {len(handler.pois):,}")
    
    total_items = (len(handler.admin_boundaries) + len(handler.streets) + 
                   len(handler.buildings) + len(handler.pois))
    print(f"\n   Total items to import: {total_items:,}")
    
    # STEP 2: Database import
    print_step(2, "IMPORTING TO DATABASE")
    
    print(f"\nConnecting to PostgreSQL database...")
    engine = create_engine(settings.SQLALCHEMY_SYNC_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    print(f"Database connection established")
    
    start_import = time.time()
    
    try:
        # Import administrative boundaries
        if handler.admin_boundaries:
            print(f"\nImporting Administrative Boundaries...")
            print(f"   Total: {len(handler.admin_boundaries)} boundaries")
            
            for idx, data in enumerate(handler.admin_boundaries, 1):
                boundary = AdministrativeBoundary(
                    osm_id=data['osm_id'],
                    osm_type=data['osm_type'],
                    name=data['name'],
                    name_en=data['name_en'],
                    admin_level=data['admin_level'],
                    tags=data['tags'],
                    # geometry will be added in post-processing
                )
                session.add(boundary)
                
                if idx % 10 == 0:
                    print(f"   Progress: {idx}/{len(handler.admin_boundaries)} ({idx*100//len(handler.admin_boundaries)}%)")
            
            session.commit()
            print(f"  Imported {len(handler.admin_boundaries)} boundaries")
        else:
            print(f"\n No administrative boundaries found")
        
        # Import streets
        if handler.streets:
            print(f"\n🛣️  Importing Streets...")
            print(f"   Total: {len(handler.streets):,} streets")
            
            batch_size = 1000
            start_streets = time.time()
            
            for idx, data in enumerate(handler.streets, 1):
                street = Street(
                    osm_id=data['osm_id'],
                    osm_type=data['osm_type'],
                    name=data['name'],
                    name_en=data['name_en'],
                    highway_type=data['highway_type'],
                    surface=data['surface'],
                    lanes=data['lanes'],
                    maxspeed=data['maxspeed'],
                    oneway=data['oneway'],
                    geometry=WKTElement(data['geometry_wkt'], srid=4326),
                    tags=data['tags']
                )
                session.add(street)
                
                if idx % batch_size == 0:
                    session.commit()
                    elapsed = time.time() - start_streets
                    speed = idx / elapsed if elapsed > 0 else 0
                    remaining = (len(handler.streets) - idx) / speed if speed > 0 else 0
                    print(f"   Progress: {idx:,}/{len(handler.streets):,} ({idx*100//len(handler.streets)}%) | {speed:.0f} items/s | ETA: {remaining:.0f}s")
            
            session.commit()
            streets_duration = time.time() - start_streets
            print(f"   Imported {len(handler.streets):,} streets in {streets_duration:.1f}s")
        else:
            print(f"\n No streets found")
        
        # Import buildings
        if handler.buildings:
            print(f"\nImporting Buildings...")
            print(f"   Total: {len(handler.buildings):,} buildings")
            
            start_buildings = time.time()
            
            for idx, data in enumerate(handler.buildings, 1):
                building = Building(
                    osm_id=data['osm_id'],
                    osm_type=data['osm_type'],
                    name=data['name'],
                    building_type=data['building_type'],
                    addr_street=data['addr_street'],
                    addr_housenumber=data['addr_housenumber'],
                    addr_district=data['addr_district'],
                    levels=data['levels'],
                    geometry=WKTElement(data['geometry_wkt'], srid=4326),
                    tags=data['tags']
                )
                session.add(building)
                
                if idx % batch_size == 0:
                    session.commit()
                    elapsed = time.time() - start_buildings
                    speed = idx / elapsed if elapsed > 0 else 0
                    remaining = (len(handler.buildings) - idx) / speed if speed > 0 else 0
                    print(f"   Progress: {idx:,}/{len(handler.buildings):,} ({idx*100//len(handler.buildings)}%) | {speed:.0f} items/s | ETA: {remaining:.0f}s")
            
            session.commit()
            buildings_duration = time.time() - start_buildings
            print(f"   Imported {len(handler.buildings):,} buildings in {buildings_duration:.1f}s")
        else:
            print(f"\nNo buildings found")
        
        # Import POIs
        if handler.pois:
            print(f"\nImporting POIs...")
            print(f"   Total: {len(handler.pois):,} POIs")
            
            batch_size = 1000
            start_pois = time.time()
            
            for idx, data in enumerate(handler.pois, 1):
                poi = POI(
                    osm_id=data['osm_id'],
                    osm_type=data['osm_type'],
                    name=data['name'],
                    name_en=data['name_en'],
                    category=data['category'],
                    subcategory=data['subcategory'],
                    phone=data['phone'],
                    website=data['website'],
                    email=data['email'],
                    opening_hours=data['opening_hours'],
                    location=WKTElement(data['geometry_wkt'], srid=4326),
                    tags=data['tags']
                )
                session.add(poi)
                
                if idx % batch_size == 0:
                    session.commit()
                    elapsed = time.time() - start_pois
                    speed = idx / elapsed if elapsed > 0 else 0
                    remaining = (len(handler.pois) - idx) / speed if speed > 0 else 0
                    print(f"   Progress: {idx:,}/{len(handler.pois):,} ({idx*100//len(handler.pois)}%) | {speed:.0f} items/s | ETA: {remaining:.0f}s")
            
            session.commit()
            pois_duration = time.time() - start_pois
            print(f"   Imported {len(handler.pois):,} POIs in {pois_duration:.1f}s")
        else:
            print(f"\n No POIs found")
        
        # Final summary
        total_import_time = time.time() - start_import
        
        print_separator(" IMPORT COMPLETED SUCCESSFULLY")
        
        print(f"\n Final Statistics:")
        print(f"   ├─ Administrative Boundaries: {len(handler.admin_boundaries):,}")
        print(f"   ├─ Streets: {len(handler.streets):,}")
        print(f"   ├─ Buildings: {len(handler.buildings):,}")
        print(f"   └─ POIs: {len(handler.pois):,}")
        
        total_items = (len(handler.admin_boundaries) + len(handler.streets) + 
                       len(handler.buildings) + len(handler.pois))
        print(f"\n   Total items imported: {total_items:,}")
        print(f"   Total import time: {total_import_time:.1f} seconds")
        print(f"   Average speed: {total_items/total_import_time:.0f} items/second")
        
        print_separator()
        
        return True
        
    except Exception as e:
        print(f" Error importing data: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    import_hanoi_osm()
