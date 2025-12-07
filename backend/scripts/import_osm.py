#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Import OSM data từ vietnam-latest.osm.pbf vào PostgreSQL/PostGIS
Sử dụng osmium tool để extract và parse data

Usage:
    python scripts/import_osm.py [--area hanoi] [--limit 10000]
"""

import sys
import os
import argparse
import subprocess
import json
from typing import Dict, List, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.models.geographic import AdministrativeBoundary, Street, Building, POI


class OSMImporter:
    """Import OSM data vào database"""
    
    def __init__(self, osm_file: str):
        self.osm_file = osm_file
        self.engine = create_engine(settings.SQLALCHEMY_SYNC_DATABASE_URI)
        self.session = Session(self.engine)
        
    def check_osmium(self):
        """Check osmium tool có sẵn không"""
        try:
            result = subprocess.run(['osmium', '--version'], 
                                    capture_output=True, text=True, check=True)
            print(f"✓ Osmium version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Osmium tool not found! Install it first:")
            print("   Ubuntu/Debian: sudo apt install osmium-tool")
            print("   macOS: brew install osmium-tool")
            return False
    
    def extract_admin_boundaries(self, limit: int = None):
        """Extract administrative boundaries (admin_level=4,5,6,7)"""
        print("\n📍 Extracting administrative boundaries...")
        
        # Use osmium to extract admin boundaries
        cmd = [
            'osmium', 'tags-filter',
            self.osm_file,
            'r/boundary=administrative',
            '-o', '/tmp/admin_boundaries.osm.pbf', '-f', 'pbf'
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print("✓ Extracted admin boundaries to temporary file")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extracting: {e}")
            return
        
        # Convert to GeoJSON for easier parsing
        cmd = [
            'osmium', 'export',
            '/tmp/admin_boundaries.osm.pbf',
            '-o', '/tmp/admin_boundaries.geojson',
            '-f', 'geojson'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Parse GeoJSON and import
        with open('/tmp/admin_boundaries.geojson', 'r') as f:
            geojson_data = json.load(f)
        
        count = 0
        for feature in geojson_data.get('features', []):
            if limit and count >= limit:
                break
                
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            # Only import if has admin_level
            admin_level = props.get('admin_level')
            if not admin_level or admin_level not in ['4', '5', '6', '7', '8']:
                continue
            
            name = props.get('name') or props.get('name:vi') or props.get('name:en')
            if not name:
                continue
            
            # Create WKT from GeoJSON geometry
            from shapely.geometry import shape
            from shapely import wkt
            geom_shapely = shape(geom)
            geom_wkt = wkt.dumps(geom_shapely)
            
            # Get OSM ID from feature id or generate from coordinates
            osm_id = feature.get('id', 0)
            if not osm_id or osm_id == 0:
                # Generate pseudo-ID from coordinates
                import hashlib
                coord_str = f"{name}_{admin_level}_{geom_shapely.centroid.x}_{geom_shapely.centroid.y}"
                osm_id = int(hashlib.md5(coord_str.encode()).hexdigest()[:12], 16)
            
            boundary = AdministrativeBoundary(
                osm_id=osm_id,
                osm_type=feature.get('type', 'relation'),
                name=name,
                name_en=props.get('name:en'),
                admin_level=int(admin_level),
                geometry=WKTElement(geom_wkt, srid=4326),
                tags=props,
                population=int(props.get('population')) if props.get('population') else None
            )
            
            self.session.add(boundary)
            count += 1
            
            if count % 100 == 0:
                self.session.commit()
                print(f"  → Imported {count} boundaries...")
        
        self.session.commit()
        print(f"✅ Imported {count} administrative boundaries")
    
    def extract_streets(self, limit: int = None):
        """Extract streets (highway tags)"""
        print("\n🛣️  Extracting streets...")
        
        # Extract highways
        cmd = [
            'osmium', 'tags-filter',
            self.osm_file,
            'w/highway',
            '-o', '/tmp/streets.osm.pbf', '-f', 'pbf'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Convert to GeoJSON
        cmd = [
            'osmium', 'export',
            '/tmp/streets.osm.pbf',
            '-o', '/tmp/streets.geojson',
            '-f', 'geojson'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Parse and import
        with open('/tmp/streets.geojson', 'r') as f:
            geojson_data = json.load(f)
        
        count = 0
        for feature in geojson_data.get('features', []):
            if limit and count >= limit:
                break
            
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            highway_type = props.get('highway')
            if not highway_type:
                continue
            
            # Calculate length
            from shapely.geometry import shape
            from shapely import wkt
            geom_shapely = shape(geom)
            geom_wkt = wkt.dumps(geom_shapely)
            
            # Length in meters (approximate)
            import pyproj
            geod = pyproj.Geod(ellps='WGS84')
            length = abs(geod.geometry_length(geom_shapely))
            
            # Get OSM ID
            osm_id = feature.get('id', 0)
            if not osm_id:
                import hashlib
                coord_str = f"{props.get('name', 'street')}_{geom_shapely.centroid.x}_{geom_shapely.centroid.y}"
                osm_id = int(hashlib.md5(coord_str.encode()).hexdigest()[:12], 16)
            
            street = Street(
                osm_id=osm_id,
                osm_type=feature.get('type', 'way'),
                name=props.get('name'),
                name_en=props.get('name:en'),
                highway_type=highway_type,
                surface=props.get('surface'),
                lanes=int(props.get('lanes')) if props.get('lanes') else None,
                maxspeed=int(props.get('maxspeed')) if props.get('maxspeed') and props.get('maxspeed').isdigit() else None,
                oneway=props.get('oneway') == 'yes',
                geometry=WKTElement(geom_wkt, srid=4326),
                length=length,
                tags=props
            )
            
            self.session.add(street)
            count += 1
            
            if count % 500 == 0:
                self.session.commit()
                print(f"  → Imported {count} streets...")
        
        self.session.commit()
        print(f"✅ Imported {count} streets")
    
    def extract_buildings(self, limit: int = None):
        """Extract buildings"""
        print("\n🏢 Extracting buildings...")
        
        cmd = [
            'osmium', 'tags-filter',
            self.osm_file,
            'w/building',
            '-o', '/tmp/buildings.osm.pbf', '-f', 'pbf'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        cmd = [
            'osmium', 'export',
            '/tmp/buildings.osm.pbf',
            '-o', '/tmp/buildings.geojson',
            '-f', 'geojson'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        with open('/tmp/buildings.geojson', 'r') as f:
            geojson_data = json.load(f)
        
        count = 0
        for feature in geojson_data.get('features', []):
            if limit and count >= limit:
                break
            
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            building_type = props.get('building', 'yes')
            
            from shapely.geometry import shape
            from shapely import wkt
            geom_shapely = shape(geom)
            geom_wkt = wkt.dumps(geom_shapely)
            
            # Calculate area in square meters
            area = geom_shapely.area * 111320 * 111320  # Approximate conversion
            
            # Get OSM ID
            osm_id = feature.get('id', 0)
            if not osm_id:
                import hashlib
                coord_str = f"{props.get('name', 'building')}_{geom_shapely.centroid.x}_{geom_shapely.centroid.y}"
                osm_id = int(hashlib.md5(coord_str.encode()).hexdigest()[:12], 16)
            
            building = Building(
                osm_id=osm_id,
                osm_type=feature.get('type', 'way'),
                name=props.get('name'),
                building_type=building_type,
                addr_street=props.get('addr:street'),
                addr_housenumber=props.get('addr:housenumber'),
                addr_district=props.get('addr:district'),
                levels=int(props.get('building:levels')) if props.get('building:levels') else None,
                height=float(props.get('height')) if props.get('height') else None,
                geometry=WKTElement(geom_wkt, srid=4326),
                area=area,
                tags=props
            )
            
            self.session.add(building)
            count += 1
            
            if count % 1000 == 0:
                self.session.commit()
                print(f"  → Imported {count} buildings...")
        
        self.session.commit()
        print(f"✅ Imported {count} buildings")
    
    def extract_pois(self, limit: int = None):
        """Extract Points of Interest (amenities, shops, tourism, etc.)"""
        print("\n📍 Extracting POIs...")
        
        # Extract amenities, shops, tourism, leisure
        cmd = [
            'osmium', 'tags-filter',
            self.osm_file,
            'n/amenity', 'n/shop', 'n/tourism', 'n/leisure',
            '-o', '/tmp/pois.osm.pbf', '-f', 'pbf'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        cmd = [
            'osmium', 'export',
            '/tmp/pois.osm.pbf',
            '-o', '/tmp/pois.geojson',
            '-f', 'geojson'
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        with open('/tmp/pois.geojson', 'r') as f:
            geojson_data = json.load(f)
        
        count = 0
        for feature in geojson_data.get('features', []):
            if limit and count >= limit:
                break
            
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            # Determine category and subcategory
            category = None
            subcategory = None
            
            if props.get('amenity'):
                category = 'amenity'
                subcategory = props.get('amenity')
            elif props.get('shop'):
                category = 'shop'
                subcategory = props.get('shop')
            elif props.get('tourism'):
                category = 'tourism'
                subcategory = props.get('tourism')
            elif props.get('leisure'):
                category = 'leisure'
                subcategory = props.get('leisure')
            
            if not category:
                continue
            
            from shapely.geometry import shape
            from shapely import wkt
            geom_shapely = shape(geom)
            geom_wkt = wkt.dumps(geom_shapely)
            
            # Get OSM ID
            osm_id = feature.get('id', 0)
            if not osm_id:
                import hashlib
                coord_str = f"{category}_{subcategory}_{geom_shapely.x}_{geom_shapely.y}"
                osm_id = int(hashlib.md5(coord_str.encode()).hexdigest()[:12], 16)
            
            poi = POI(
                osm_id=osm_id,
                osm_type=feature.get('type', 'node'),
                name=props.get('name'),
                name_en=props.get('name:en'),
                category=category,
                subcategory=subcategory,
                phone=props.get('phone'),
                website=props.get('website'),
                email=props.get('email'),
                address=props.get('addr:full') or props.get('addr:street'),
                location=WKTElement(geom_wkt, srid=4326),
                tags=props,
                opening_hours=props.get('opening_hours')
            )
            
            self.session.add(poi)
            count += 1
            
            if count % 500 == 0:
                self.session.commit()
                print(f"  → Imported {count} POIs...")
        
        self.session.commit()
        print(f"✅ Imported {count} POIs")
    
    def import_all(self, limit: int = None):
        """Import all OSM data types"""
        print(f"\n🚀 Starting OSM import from: {self.osm_file}")
        print(f"   Limit per type: {limit if limit else 'No limit'}\n")
        
        if not self.check_osmium():
            return False
        
        if not os.path.exists(self.osm_file):
            print(f"❌ OSM file not found: {self.osm_file}")
            return False
        
        try:
            self.extract_admin_boundaries(limit)
            self.extract_streets(limit)
            self.extract_buildings(limit)
            self.extract_pois(limit)
            
            print("\n✅ OSM import completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error during import: {e}")
            self.session.rollback()
            return False
        finally:
            self.session.close()


def main():
    parser = argparse.ArgumentParser(description='Import OSM data to PostgreSQL')
    parser.add_argument('--file', default='/app/data/osm/vietnam-latest.osm.pbf',
                        help='Path to OSM PBF file')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of items per type (for testing)')
    
    args = parser.parse_args()
    
    importer = OSMImporter(args.file)
    success = importer.import_all(limit=args.limit)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
