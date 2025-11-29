#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Import OSM data vào PostgreSQL + PostGIS
Requires: osmium, shapely, psycopg2, geoalchemy2
Install: pip install osmium shapely psycopg2-binary geoalchemy2

Chạy: python scripts/import_osm.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import osmium
import osmium.geom
from shapely.wkb import loads
from shapely import wkt
from sqlalchemy.orm import Session
from app.db.postgres import SessionLocal, engine
from app.db.base import Base
from app.models.geographic import AdministrativeBoundary, Street, Building
from app.models.facility import PublicFacility, TransportFacility

# Create tables if not exists
Base.metadata.create_all(bind=engine)


class OSMHandler(osmium.SimpleHandler):
    """Handler để parse OSM data"""
    
    def __init__(self, db_session: Session):
        osmium.SimpleHandler.__init__(self)
        self.db = db_session
        self.areas_count = 0
        self.streets_count = 0
        self.buildings_count = 0
        self.pois_count = 0
        
        # Create WKB factory for geometry conversion
        self.wkb_factory = osmium.geom.WKBFactory()
        
    def area(self, a):
        """Import administrative boundaries"""
        tags = {t.k: t.v for t in a.tags}
        
        if 'admin_level' in tags:
            try:
                admin_level = int(tags.get('admin_level'))
            except ValueError:
                return
            
            # Only import: 4=city, 6=district, 8=ward
            if admin_level not in [4, 6, 8]:
                return
            
            try:
                # Get geometry as WKB using WKBFactory
                wkb = self.wkb_factory.create_multipolygon(a)
                geom = loads(wkb, hex=False)
                
                # Check if already exists
                existing = self.db.query(AdministrativeBoundary).filter(
                    AdministrativeBoundary.osm_id == a.id
                ).first()
                
                if existing:
                    return
                
                # Insert
                boundary = AdministrativeBoundary(
                    osm_id=a.id,
                    name=tags.get('name'),
                    name_en=tags.get('name:en'),
                    admin_level=admin_level,
                    boundary=f'SRID=4326;{geom.wkt}',
                    properties=tags
                )
                
                self.db.add(boundary)
                self.areas_count += 1
                
                if self.areas_count % 10 == 0:
                    self.db.commit()
                    print(f"  Imported {self.areas_count} boundaries...")
                
            except Exception as e:
                # Silently skip areas without valid geometry
                pass
    
    def way(self, w):
        """Import ways: streets, buildings, POIs"""
        tags = {t.k: t.v for t in w.tags}
        
        try:
            # Try to create linestring for streets (open ways)
            if 'highway' in tags and not w.is_closed():
                try:
                    wkb = self.wkb_factory.create_linestring(w)
                    geom = loads(wkb, hex=False)
                    self._import_street(w.id, tags, geom)
                except:
                    pass
                return
            
            # Try to create polygon for buildings and closed ways
            if w.is_closed():
                try:
                    wkb = self.wkb_factory.create_polygon(w)
                    geom = loads(wkb, hex=False)
                    
                    # Import buildings
                    if 'building' in tags:
                        self._import_building(w.id, tags, geom)
                    
                    # Import POIs
                    elif any(key in tags for key in ['amenity', 'shop', 'tourism']):
                        self._import_poi(w.id, tags, geom)
                except:
                    pass
        
        except Exception as e:
            # Silently skip ways with invalid geometry
            pass
    
    def _import_street(self, osm_id, tags, geom):
        """Import street"""
        try:
            existing = self.db.query(Street).filter(Street.osm_id == osm_id).first()
            if existing:
                return
            
            # Parse numeric fields safely
            lanes = None
            if tags.get('lanes'):
                try:
                    lanes = int(tags.get('lanes'))
                except:
                    pass
            
            maxspeed = None
            if tags.get('maxspeed'):
                try:
                    # Handle "50 mph", "30" etc
                    speed_str = tags.get('maxspeed').split()[0]
                    maxspeed = int(speed_str)
                except:
                    pass
            
            street = Street(
                osm_id=osm_id,
                name=tags.get('name'),
                name_en=tags.get('name:en'),
                street_type=tags.get('highway'),
                geometry=f'SRID=4326;{geom.wkt}',
                lanes=lanes,
                maxspeed=maxspeed,
                surface=tags.get('surface'),
                properties=tags
            )
            
            self.db.add(street)
            self.streets_count += 1
            
            if self.streets_count % 100 == 0:
                self.db.commit()
                print(f"  Imported {self.streets_count} streets...")
        except Exception as e:
            pass
    
    def _import_building(self, osm_id, tags, geom):
        """Import building"""
        try:
            existing = self.db.query(Building).filter(Building.osm_id == osm_id).first()
            if existing:
                return
            
            # Parse numeric fields safely
            levels = None
            if tags.get('building:levels'):
                try:
                    levels = int(tags.get('building:levels'))
                except:
                    pass
            
            building = Building(
                osm_id=osm_id,
                name=tags.get('name'),
                building_type=tags.get('building'),
                address=tags.get('addr:full') or tags.get('addr:street'),
                geometry=f'SRID=4326;{geom.wkt}',
                levels=levels,
                properties=tags
            )
            
            self.db.add(building)
            self.buildings_count += 1
            
            if self.buildings_count % 100 == 0:
                self.db.commit()
                print(f"  Imported {self.buildings_count} buildings...")
        except Exception as e:
            pass
    
    def _import_poi(self, osm_id, tags, geom):
        """Import POI (hospital, school, park, etc.)"""
        try:
            amenity = tags.get('amenity')
            
            # Map OSM amenity to our categories
            category_map = {
                'hospital': 'hospital',
                'clinic': 'hospital',
                'doctors': 'hospital',
                'school': 'school',
                'university': 'school',
                'college': 'school',
                'kindergarten': 'school',
                'park': 'park',
                'playground': 'park',
                'police': 'police_station',
                'fire_station': 'fire_station',
                'library': 'library',
                'marketplace': 'market',
                'bus_station': 'bus_stop',
                'taxi': 'taxi_stand',
            }
            
            category = category_map.get(amenity)
            if not category:
                return
            
            # Use shapely to get centroid
            centroid = geom.centroid
            
            # Check if transport facility
            if category in ['bus_stop', 'taxi_stand']:
                existing = self.db.query(TransportFacility).filter(
                    TransportFacility.osm_id == osm_id
                ).first()
                if existing:
                    return
                
                facility = TransportFacility(
                    osm_id=osm_id,
                    name=tags.get('name') or f"{category.title()} {osm_id}",
                    name_en=tags.get('name:en'),
                    facility_type=category,
                    location=f'SRID=4326;{centroid.wkt}',
                    properties=tags
                )
            else:
                existing = self.db.query(PublicFacility).filter(
                    PublicFacility.osm_id == osm_id
                ).first()
                if existing:
                    return
                
                facility = PublicFacility(
                    osm_id=osm_id,
                    name=tags.get('name') or f"{category.title()} {osm_id}",
                    name_en=tags.get('name:en'),
                    category=category,
                    address=tags.get('addr:full') or tags.get('addr:street'),
                    location=f'SRID=4326;{centroid.wkt}',
                    phone=tags.get('phone'),
                    website=tags.get('website'),
                    opening_hours=tags.get('opening_hours'),
                    properties=tags
                )
            
            self.db.add(facility)
            self.pois_count += 1
            
            if self.pois_count % 50 == 0:
                self.db.commit()
                print(f"  Imported {self.pois_count} POIs...")
        except Exception as e:
            pass
    
    def finalize(self):
        """Commit final changes"""
        self.db.commit()
        print(f"\n✅ Import completed!")
        print(f"  - Administrative boundaries: {self.areas_count}")
        print(f"  - Streets: {self.streets_count}")
        print(f"  - Buildings: {self.buildings_count}")
        print(f"  - POIs: {self.pois_count}")


def import_osm_data(osm_file: str):
    """Main import function"""
    if not os.path.exists(osm_file):
        print(f"❌ Error: File not found: {osm_file}")
        print(f"Run: bash scripts/download_osm.sh")
        return
    
    print(f"📦 Importing OSM data from: {osm_file}")
    
    db = SessionLocal()
    handler = OSMHandler(db)
    
    try:
        handler.apply_file(osm_file)
        handler.finalize()
    except Exception as e:
        print(f"❌ Import failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    osm_file = "data/osm/hanoi.osm.pbf"
    
    if len(sys.argv) > 1:
        osm_file = sys.argv[1]
    
    import_osm_data(osm_file)
