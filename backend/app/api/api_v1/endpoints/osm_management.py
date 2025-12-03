"""
OSM Data Management Endpoints for Hanoi

Handles downloading, processing, and importing OSM data without rate limits.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import asyncio

from app.core.database import get_db
from app.adapters.osm_local_data import HanoiOSMDataManager, HanoiOSMParser
from app.repositories.entity_repository import EntityRepository
from app.models.ngsi_ld import Entity

router = APIRouter()

@router.post("/download-osm-data", response_model=Dict[str, Any])
async def download_osm_data(
    background_tasks: BackgroundTasks
):
    """
    Download Vietnam OSM extract from Geofabrik.
    This is a one-time operation (or periodic update).
    
    File size: ~200MB
    Source: https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
    Updated: Daily by Geofabrik
    """
    manager = HanoiOSMDataManager()
    
    try:
        # Download in background
        background_tasks.add_task(_download_and_extract, manager)
        
        return {
            "status": "started",
            "message": "OSM data download started in background",
            "source": manager.VIETNAM_OSM_URL,
            "estimated_time": "5-10 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _download_and_extract(manager: HanoiOSMDataManager):
    """Background task to download and extract OSM data"""
    try:
        # Download Vietnam extract
        await manager.download_vietnam_extract()
        
        # Extract Hanoi data
        manager.extract_hanoi_data()
        
        print("✅ OSM data download and extraction complete!")
    except Exception as e:
        print(f"❌ Error downloading OSM data: {e}")

@router.post("/import-osm-data", response_model=Dict[str, Any])
async def import_osm_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Parse local OSM file and import all Hanoi data into database.
    
    This processes the downloaded OSM file and converts all entities
    to NGSI-LD format, then stores them in PostgreSQL.
    
    Expected entities:
    - Bus stops: 3,000+
    - Hospitals: 100+
    - Schools: 500+
    - Parks: 50+
    - Parking: 200+
    """
    manager = HanoiOSMDataManager()
    
    # Check if OSM file exists
    if not manager.hanoi_file.exists() and not manager.osm_file.exists():
        raise HTTPException(
            status_code=404,
            detail="OSM data file not found. Please run /download-osm-data first."
        )
    
    osm_file = manager.hanoi_file if manager.hanoi_file.exists() else manager.osm_file
    
    try:
        # Parse OSM file
        print(f"📖 Parsing OSM file: {osm_file}")
        parser = HanoiOSMParser(manager.HANOI_BBOX)
        parser.apply_file(str(osm_file))
        
        # Import entities to database
        repo = EntityRepository(db)
        results = {}
        
        # Import bus stops
        print(f"💾 Importing {len(parser.entities['bus_stops'])} bus stops...")
        saved = 0
        for entity_data in parser.entities["bus_stops"]:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved += 1
            except Exception as e:
                continue
        results["bus_stops"] = {"total": len(parser.entities["bus_stops"]), "saved": saved}
        
        # Import hospitals
        print(f"💾 Importing {len(parser.entities['hospitals'])} hospitals...")
        saved = 0
        for entity_data in parser.entities["hospitals"]:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved += 1
            except:
                continue
        results["hospitals"] = {"total": len(parser.entities["hospitals"]), "saved": saved}
        
        # Import schools
        print(f"💾 Importing {len(parser.entities['schools'])} schools...")
        saved = 0
        for entity_data in parser.entities["schools"]:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved += 1
            except:
                continue
        results["schools"] = {"total": len(parser.entities["schools"]), "saved": saved}
        
        # Import parks
        print(f"💾 Importing {len(parser.entities['parks'])} parks...")
        saved = 0
        for entity_data in parser.entities["parks"]:
            if entity_data:  # Some may be None
                try:
                    entity = Entity(**entity_data)
                    await repo.create_entity(entity)
                    saved += 1
                except:
                    continue
        results["parks"] = {"total": len(parser.entities["parks"]), "saved": saved}
        
        # Import parking
        print(f"💾 Importing {len(parser.entities['parking'])} parking areas...")
        saved = 0
        for entity_data in parser.entities["parking"]:
            if entity_data:
                try:
                    entity = Entity(**entity_data)
                    await repo.create_entity(entity)
                    saved += 1
                except:
                    continue
        results["parking"] = {"total": len(parser.entities["parking"]), "saved": saved}
        
        return {
            "status": "success",
            "source_file": str(osm_file),
            "results": results,
            "total_entities": sum(r["saved"] for r in results.values())
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/osm-data-status", response_model=Dict[str, Any])
async def get_osm_data_status():
    """
    Check status of local OSM data files.
    """
    manager = HanoiOSMDataManager()
    
    status = {
        "vietnam_file": {
            "exists": manager.osm_file.exists(),
            "path": str(manager.osm_file),
            "size_mb": round(manager.osm_file.stat().st_size / 1024 / 1024, 2) if manager.osm_file.exists() else 0
        },
        "hanoi_file": {
            "exists": manager.hanoi_file.exists(),
            "path": str(manager.hanoi_file),
            "size_mb": round(manager.hanoi_file.stat().st_size / 1024 / 1024, 2) if manager.hanoi_file.exists() else 0
        },
        "ready_to_import": manager.hanoi_file.exists() or manager.osm_file.exists()
    }
    
    return status

@router.post("/update-osm-data", response_model=Dict[str, Any])
async def update_osm_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete workflow: Download → Extract → Import
    
    This is the recommended way to refresh OSM data.
    Run this monthly or when you need fresh data.
    """
    manager = HanoiOSMDataManager()
    
    try:
        # Start download in background
        background_tasks.add_task(_full_update_workflow, manager, db)
        
        return {
            "status": "started",
            "message": "Full OSM data update started in background",
            "steps": [
                "1. Download Vietnam OSM extract (~200MB)",
                "2. Extract Hanoi data (~50MB)",
                "3. Parse and convert to NGSI-LD",
                "4. Import to database"
            ],
            "estimated_time": "10-15 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _full_update_workflow(manager: HanoiOSMDataManager, db: AsyncSession):
    """Background task for full update workflow"""
    try:
        print("🚀 Starting full OSM data update workflow...")
        
        # Step 1: Download
        print("📥 Step 1/4: Downloading Vietnam OSM extract...")
        await manager.download_vietnam_extract()
        
        # Step 2: Extract
        print("✂️  Step 2/4: Extracting Hanoi data...")
        manager.extract_hanoi_data()
        
        # Step 3 & 4: Parse and Import
        print("📖 Step 3/4: Parsing OSM data...")
        osm_file = manager.hanoi_file if manager.hanoi_file.exists() else manager.osm_file
        parser = HanoiOSMParser(manager.HANOI_BBOX)
        parser.apply_file(str(osm_file))
        
        print("💾 Step 4/4: Importing to database...")
        repo = EntityRepository(db)
        
        total_saved = 0
        for category, entities in parser.entities.items():
            for entity_data in entities:
                if entity_data:
                    try:
                        entity = Entity(**entity_data)
                        await repo.create_entity(entity)
                        total_saved += 1
                    except:
                        continue
        
        print(f"✅ Full update complete! Imported {total_saved} entities.")
        
    except Exception as e:
        print(f"❌ Update workflow failed: {e}")

