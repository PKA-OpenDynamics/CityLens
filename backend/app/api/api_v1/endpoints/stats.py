# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Statistics and Monitoring Endpoints for CityLens Backend
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from datetime import datetime
import psutil
import os

from app.core.database import get_db
from app.models.db_models import EntityDB

router = APIRouter()

@router.get("/stats")
async def get_system_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive system statistics:
    - Entity counts by type
    - Database size
    - Memory usage
    - Uptime
    """
    # Entity counts by type
    query = select(
        EntityDB.type,
        func.count(EntityDB.id).label('count')
    ).group_by(EntityDB.type)
    
    result = await db.execute(query)
    entities_by_type = {row.type: row.count for row in result}
    
    # Total entities
    total_query = select(func.count(EntityDB.id))
    total_result = await db.execute(total_query)
    total_entities = total_result.scalar()
    
    # Database size (PostgreSQL specific)
    try:
        db_size_query = text("SELECT pg_database_size(current_database())")
        db_size_result = await db.execute(db_size_query)
        db_size_bytes = db_size_result.scalar()
        db_size_mb = round(db_size_bytes / (1024 * 1024), 2)
    except Exception:
        db_size_mb = 0
    
    # System resources
    memory = psutil.virtual_memory()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "entities": {
            "total": total_entities,
            "by_type": entities_by_type
        },
        "database": {
            "size_mb": db_size_mb,
            "status": "connected"
        },
        "system": {
            "memory_usage_percent": memory.percent,
            "memory_available_mb": round(memory.available / (1024 * 1024), 2),
            "cpu_count": psutil.cpu_count(),
            "python_process_memory_mb": round(
                psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2
            )
        }
    }


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Enhanced health check endpoint for monitoring and keep-alive.
    
    Returns:
    - Database connectivity
    - OSM data availability
    - System uptime
    - Response time
    """
    start_time = datetime.utcnow()
    
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
        db_healthy = True
        db_message = "Database connected"
    except Exception as e:
        db_healthy = False
        db_message = f"Database error: {str(e)}"
    
    # Check entities count
    try:
        total_query = select(func.count(EntityDB.id))
        result = await db.execute(total_query)
        total_entities = result.scalar()
    except Exception:
        total_entities = 0
    
    # Check OSM data availability
    osm_data_imported = total_entities > 100  # Assume OSM imported if >100 entities
    
    response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "healthy": db_healthy,
            "message": db_message,
            "entities_count": total_entities
        },
        "osm_data": {
            "imported": osm_data_imported,
            "status": "ready" if osm_data_imported else "pending"
        },
        "performance": {
            "response_time_ms": round(response_time_ms, 2)
        }
    }


@router.get("/types")
async def list_entity_types(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    List all available entity types with counts.
    Useful for discovering what data is available.
    """
    query = select(
        EntityDB.type,
        func.count(EntityDB.id).label('count')
    ).group_by(EntityDB.type).order_by(func.count(EntityDB.id).desc())
    
    result = await db.execute(query)
    types = [{"type": row.type, "count": row.count} for row in result]
    
    return {
        "total_types": len(types),
        "types": types
    }


@router.get("/examples/{entity_type}")
async def get_entity_examples(
    entity_type: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get example entities of a specific type.
    Useful for understanding data structure.
    """
    query = select(EntityDB).where(
        EntityDB.type == entity_type
    ).limit(limit)
    
    result = await db.execute(query)
    entities = result.scalars().all()
    
    if not entities:
        return {
            "type": entity_type,
            "count": 0,
            "examples": []
        }
    
    return {
        "type": entity_type,
        "count": len(entities),
        "examples": [e.data for e in entities]
    }
