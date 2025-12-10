# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
NGSI-LD Entity Service
Automatic synchronization of real-time data to NGSI-LD entities
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.db_models import EntityDB
from app.adapters.openweathermap import OpenWeatherMapAdapter
from app.adapters.aqicn import AQICNAdapter
from app.schemas.fiware.weather import WeatherObservedCreate, to_ngsi_ld_entity as weather_to_ngsi_ld
from app.schemas.fiware.air_quality import AirQualityObservedCreate, to_ngsi_ld_entity as aqi_to_ngsi_ld


class NGSILDEntityService:
    """Service for managing NGSI-LD entities"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def store_entity(self, entity_data: Dict[str, Any]) -> EntityDB:
        """
        Store or update NGSI-LD entity in database.
        """
        entity_id = entity_data["id"]
        entity_type = entity_data["type"]
        
        # Check if exists
        result = await self.db.execute(
            select(EntityDB).where(EntityDB.id == entity_id)
        )
        existing = result.scalar_one_or_none()
        
        # Extract geometry
        geometry_wkt = self._extract_geometry(entity_data)
        
        if existing:
            # Update
            existing.data = entity_data
            existing.location_geom = geometry_wkt
            existing.modified_at = datetime.utcnow()
            await self.db.commit()
            return existing
        else:
            # Create
            entity = EntityDB(
                id=entity_id,
                type=entity_type,
                data=entity_data,
                location_geom=geometry_wkt,
                created_at=datetime.utcnow()
            )
            self.db.add(entity)
            await self.db.commit()
            return entity
    
    async def sync_weather_data(self, lat: float, lon: float, city: str = "Hanoi") -> EntityDB:
        """
        Fetch weather data from OpenWeatherMap and store as NGSI-LD entity.
        """
        adapter = OpenWeatherMapAdapter()
        
        # Fetch data
        ngsi_ld_entity, sosa_observations = await adapter.fetch_weather(lat, lon, city)
        
        # Store in database
        return await self.store_entity(ngsi_ld_entity)
    
    async def sync_air_quality_data(self, city: str = "hanoi") -> EntityDB:
        """
        Fetch air quality data from AQICN and store as NGSI-LD entity.
        """
        adapter = AQICNAdapter()
        
        # Fetch data
        ngsi_ld_entity, sosa_observations = await adapter.fetch_city_data(city)
        
        # Store in database
        return await self.store_entity(ngsi_ld_entity)
    
    def _extract_geometry(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract geometry from NGSI-LD entity for PostGIS storage.
        Returns WKT string.
        """
        if "location" not in entity_data:
            return None
        
        location = entity_data["location"]
        if location.get("type") != "GeoProperty":
            return None
        
        geojson = location.get("value", {})
        geom_type = geojson.get("type")
        coords = geojson.get("coordinates")
        
        if not geom_type or not coords:
            return None
        
        # Convert GeoJSON to WKT
        if geom_type == "Point":
            return f"SRID=4326;POINT({coords[0]} {coords[1]})"
        elif geom_type == "LineString":
            points = ", ".join([f"{c[0]} {c[1]}" for c in coords])
            return f"SRID=4326;LINESTRING({points})"
        elif geom_type == "Polygon":
            rings = []
            for ring in coords:
                points = ", ".join([f"{c[0]} {c[1]}" for c in ring])
                rings.append(f"({points})")
            return f"SRID=4326;POLYGON({', '.join(rings)})"
        
        return None
