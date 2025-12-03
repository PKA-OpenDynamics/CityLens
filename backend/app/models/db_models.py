from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from app.core.config import settings
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class EntityDB(Base):
    """
    The 'Hybrid' Table:
    - Uses SQL columns for frequent queries (id, type, modified_at).
    - Uses PostGIS Geometry for high-performance Map queries.
    - Uses JSONB for the full NGSI-LD payload (flexible schema).
    """
    __tablename__ = "entities"

    id = Column(String, primary_key=True, index=True) # URN
    type = Column(String, index=True, nullable=False)
    
    # Store the full NGSI-LD document here
    data = Column(JSONB, nullable=False)
    
    # Geospatial Indexing (SRID 4326 = WGS84 Latitude/Longitude)
    location_geom = Column(Geometry('GEOMETRY', srid=4326), index=True, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_ngsi_ld(self):
        """Return the JSONB data as the API response"""
        return self.data

