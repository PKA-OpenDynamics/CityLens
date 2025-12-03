from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
import json

from app.models.db_models import EntityDB
from app.models.ngsi_ld import Entity

class EntityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_entity(self, entity_data: Entity) -> EntityDB:
        """
        Create a new NGSI-LD Entity.
        Handles extraction of Geometry from GeoProperty if present.
        """
        # Convert Pydantic model to dict
        data_dict = entity_data.to_dict()
        
        # Extract Geometry if available
        location_geom = None
        if entity_data.location and entity_data.location.value:
            try:
                # Convert GeoJSON dict to Shapely shape, then to WKBElement
                shapely_geom = shape(entity_data.location.value)
                location_geom = from_shape(shapely_geom, srid=4326)
            except Exception as e:
                # Logic to handle invalid geojson, for now log or ignore
                print(f"Error parsing geometry: {e}")

        db_entity = EntityDB(
            id=entity_data.id,
            type=entity_data.type,
            data=data_dict,
            location_geom=location_geom
        )
        
        self.db.add(db_entity)
        try:
            await self.db.commit()
            await self.db.refresh(db_entity)
            return db_entity
        except IntegrityError:
            await self.db.rollback()
            raise ValueError(f"Entity with id {entity_data.id} already exists.")
    
    async def upsert_entity(self, entity_data: Union[Entity, Dict[str, Any]]) -> EntityDB:
        """
        Create or update an NGSI-LD Entity.
        If entity exists, update it; otherwise create new one.
        
        Args:
            entity_data: Entity object or dict representation
        """
        # Convert dict to Entity if needed
        if isinstance(entity_data, dict):
            entity_data = Entity(**entity_data)
        
        # Check if entity exists
        existing = await self.get_entity(entity_data.id)
        
        if existing:
            # Update existing entity
            data_dict = entity_data.to_dict()
            
            # Extract Geometry if available
            location_geom = None
            if entity_data.location and entity_data.location.value:
                try:
                    shapely_geom = shape(entity_data.location.value)
                    location_geom = from_shape(shapely_geom, srid=4326)
                except Exception as e:
                    print(f"Error parsing geometry: {e}")
            
            existing.type = entity_data.type
            existing.data = data_dict
            if location_geom:
                existing.location_geom = location_geom
            
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Create new entity
            return await self.create_entity(entity_data)

    async def get_entity(self, entity_id: str) -> Optional[EntityDB]:
        stmt = select(EntityDB).where(EntityDB.id == entity_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_entities(
        self, 
        type: Optional[str] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[EntityDB]:
        stmt = select(EntityDB)
        if type:
            stmt = stmt.where(EntityDB.type == type)
        
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_entities_near(
        self, 
        latitude: float, 
        longitude: float, 
        radius_meters: float,
        type: Optional[str] = None
    ) -> List[EntityDB]:
        """
        Find entities within a radius (in meters).
        Uses PostGIS ST_DWithin with geography casting for accurate meter-based queries.
        """
        from geoalchemy2 import Geography
        from sqlalchemy import cast
        
        # Create a point using ST_SetSRID and ST_MakePoint
        point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        
        # Cast both geometries to geography for meter-based distance
        stmt = select(EntityDB).where(
            EntityDB.location_geom.isnot(None)
        ).where(
            func.ST_DWithin(
                cast(EntityDB.location_geom, Geography),
                cast(point, Geography),
                radius_meters
            )
        )
        
        if type:
            stmt = stmt.where(EntityDB.type == type)
        
        # Order by distance (closest first)
        stmt = stmt.order_by(
            func.ST_Distance(
                cast(EntityDB.location_geom, Geography),
                cast(point, Geography)
            )
        )
            
        result = await self.db.execute(stmt)
        return result.scalars().all()

