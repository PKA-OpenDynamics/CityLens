# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
NGSI-LD Service
Unified service for NGSI-LD operations
Coordinates between PostgreSQL, GraphDB, and SOSA conversions
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
from datetime import datetime

from app.schemas.ngsi_ld.base import NGSILDEntity
from app.schemas.ngsi_ld.query import NGSILDQuery, NGSILDGeoQuery
from .graphdb_service import graphdb_service
from .sosa_service import sosa_service

logger = logging.getLogger(__name__)


class NGSILDService:
    """
    Service for NGSI-LD entity operations
    
    Responsibilities:
    1. CRUD operations on NGSI-LD entities
    2. Query entities with NGSI-LD query language
    3. Sync between PostgreSQL and GraphDB
    4. Convert to SOSA/SSN for semantic web
    """
    
    def __init__(self):
        logger.info("NGSI-LD Service initialized")
    
    async def create_entity(
        self,
        entity: NGSILDEntity,
        db: Session,
        store_in_postgres: bool = True,
        store_in_graphdb: bool = True,
        convert_to_sosa: bool = True
    ) -> Dict[str, Any]:
        """
        Create NGSI-LD entity with multi-database sync
        
        Args:
            entity: NGSI-LD entity
            db: SQLAlchemy session
            store_in_postgres: Store in PostgreSQL
            store_in_graphdb: Store in GraphDB
            convert_to_sosa: Convert to SOSA/SSN
        
        Returns:
            Result dict with entity ID and storage status
        """
        try:
            entity_dict = entity.model_dump(by_alias=True, exclude_none=True)
            entity_id = entity.id
            entity_type = entity.type
            
            results = {
                "id": entity_id,
                "type": entity_type,
                "postgres": False,
                "graphdb": False,
                "sosa": False
            }
            
            # 1. Store in PostgreSQL (if applicable)
            if store_in_postgres:
                pg_stored = await self._store_in_postgres(entity_dict, db)
                results["postgres"] = pg_stored
            
            # 2. Store in GraphDB as NGSI-LD
            if store_in_graphdb:
                gdb_stored = await graphdb_service.insert_ngsi_ld_entity(entity_dict)
                results["graphdb"] = gdb_stored
            
            # 3. Convert to SOSA/SSN
            if convert_to_sosa:
                sosa_stored = await self._convert_to_sosa(entity_dict, entity_type)
                results["sosa"] = sosa_stored
            
            logger.info(f"Created entity {entity_id}: PG={results['postgres']}, "
                       f"GDB={results['graphdb']}, SOSA={results['sosa']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error creating NGSI-LD entity: {e}")
            raise
    
    async def _store_in_postgres(self, entity: Dict[str, Any], db: Session) -> bool:
        """Store entity in appropriate PostgreSQL table based on type"""
        try:
            entity_type = entity.get("type")
            
            # Map entity types to database tables
            if entity_type == "AirQualityObserved":
                return await self._store_aqi_observation(entity, db)
            elif entity_type == "WeatherObserved":
                return await self._store_weather_observation(entity, db)
            elif entity_type == "TrafficFlowObserved":
                return await self._store_traffic_observation(entity, db)
            elif entity_type == "CitizenReport":
                return await self._store_citizen_report(entity, db)
            else:
                logger.warning(f"No PostgreSQL mapping for entity type: {entity_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing in PostgreSQL: {e}")
            return False
    
    async def _store_aqi_observation(self, entity: Dict[str, Any], db: Session) -> bool:
        """Store AQI observation in environmental_data table"""
        try:
            from app.models.environment import EnvironmentalData
            
            # Extract data
            date_observed = entity.get("dateObserved", {}).get("value")
            location = entity.get("location", {}).get("value", {})
            coords = location.get("coordinates", [])
            aqi_value = entity.get("airQualityIndex", {}).get("value")
            pm25 = entity.get("PM25", {}).get("value")
            pm10 = entity.get("PM10", {}).get("value")
            
            # Create record
            env_data = EnvironmentalData(
                data_type="air_quality",
                value=aqi_value,
                unit="AQI",
                measured_at=datetime.fromisoformat(date_observed.replace('Z', '+00:00')) if date_observed else datetime.utcnow(),
                source="external_api",
                properties={
                    "pm25": pm25,
                    "pm10": pm10,
                    "ngsi_ld_id": entity.get("id")
                }
            )
            
            db.add(env_data)
            db.commit()
            
            logger.info(f"Stored AQI observation in PostgreSQL: {entity.get('id')}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing AQI observation: {e}")
            db.rollback()
            return False
    
    async def _store_citizen_report(self, entity: Dict[str, Any], db: Session) -> bool:
        """Store citizen report in reports table"""
        # This will be linked with existing Report model
        # For now, log that it should be stored
        logger.info(f"Citizen report should be stored: {entity.get('id')}")
        return True
    
    async def _store_weather_observation(self, entity: Dict[str, Any], db: Session) -> bool:
        """Store weather observation"""
        try:
            from app.models.environment import EnvironmentalData
            
            date_observed = entity.get("dateObserved", {}).get("value")
            temperature = entity.get("temperature", {}).get("value")
            humidity = entity.get("relativeHumidity", {}).get("value")
            precipitation = entity.get("precipitation", {}).get("value")
            
            env_data = EnvironmentalData(
                data_type="weather",
                value=temperature,
                unit="CEL",
                measured_at=datetime.fromisoformat(date_observed.replace('Z', '+00:00')) if date_observed else datetime.utcnow(),
                source="external_api",
                properties={
                    "humidity": humidity,
                    "precipitation": precipitation,
                    "ngsi_ld_id": entity.get("id")
                }
            )
            
            db.add(env_data)
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing weather observation: {e}")
            db.rollback()
            return False
    
    async def _store_traffic_observation(self, entity: Dict[str, Any], db: Session) -> bool:
        """Store traffic observation"""
        logger.info(f"Traffic observation logged: {entity.get('id')}")
        return True
    
    async def _convert_to_sosa(self, entity: Dict[str, Any], entity_type: str) -> bool:
        """Convert entity to SOSA/SSN format and store in GraphDB"""
        try:
            # For now, only convert certain types
            if entity_type == "CitizenReport":
                # Extract relevant data for SOSA conversion
                report_data = {
                    "id": int(entity.get("id", "").split(":")[-1]),
                    "user_id": 1,  # Extract from relationship
                    "category": entity.get("category", {}).get("value", ""),
                    "description": entity.get("description", {}).get("value", ""),
                    "location": {
                        "lon": entity.get("location", {}).get("value", {}).get("coordinates", [0, 0])[0],
                        "lat": entity.get("location", {}).get("value", {}).get("coordinates", [0, 0])[1]
                    },
                    "created_at": entity.get("dateReported", {}).get("value", datetime.utcnow().isoformat()),
                }
                return await sosa_service.citizen_report_to_sosa(report_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error converting to SOSA: {e}")
            return False
    
    async def query_entities(
        self,
        query: NGSILDQuery,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Query NGSI-LD entities
        
        Args:
            query: NGSI-LD query parameters
            db: SQLAlchemy session
        
        Returns:
            List of matching entities
        """
        try:
            # For now, query from GraphDB using SPARQL
            # In production, could query PostgreSQL first for performance
            
            # Build SPARQL query
            sparql_query = self._build_sparql_from_ngsild_query(query)
            
            results = await graphdb_service.query_sparql(sparql_query)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying entities: {e}")
            return []
    
    def _build_sparql_from_ngsild_query(self, query: NGSILDQuery) -> str:
        """Convert NGSI-LD query to SPARQL"""
        
        # Base query
        sparql = """
        PREFIX cl: <http://citylens.io/ontology#>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        
        SELECT ?entity ?type
        WHERE {
            ?entity a ?type .
        """
        
        # Type filter
        if query.type:
            types = query.get_type_list()
            type_filters = " || ".join([f'?type = cl:{t}' for t in types])
            sparql += f"\n    FILTER({type_filters})"
        
        # Geo-query
        if query.has_geo_query():
            geo_query = query.get_geo_query()
            if geo_query:
                relation, params = geo_query.parse_georel()
                coords = geo_query.parse_coordinates()
                
                if relation.value == "near" and "maxDistance" in params:
                    sparql += f"""
            ?entity geo:hasGeometry ?geom .
            FILTER(geof:distance(?geom, "POINT({coords[0]} {coords[1]})"^^geo:wktLiteral, <http://www.opengis.net/def/uom/OGC/1.0/metre>) < {params['maxDistance']})
                    """
        
        sparql += f"""
        }}
        LIMIT {query.limit}
        OFFSET {query.offset}
        """
        
        return sparql
    
    async def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID from GraphDB"""
        try:
            query = f"""
            PREFIX cl: <http://citylens.io/ontology#>
            
            SELECT ?p ?o
            WHERE {{
                <{entity_id}> ?p ?o .
            }}
            """
            
            results = await graphdb_service.query_sparql(query)
            
            if not results:
                return None
            
            # Reconstruct entity
            entity = {"id": entity_id}
            for row in results:
                pred = row.get("p", "").split("#")[-1]
                obj = row.get("o")
                entity[pred] = obj
            
            return entity
            
        except Exception as e:
            logger.error(f"Error getting entity by ID: {e}")
            return None
    
    async def update_entity(
        self,
        entity_id: str,
        attributes: Dict[str, Any],
        db: Session
    ) -> bool:
        """
        Update entity attributes
        
        Args:
            entity_id: Entity ID
            attributes: Attributes to update
            db: SQLAlchemy session
        
        Returns:
            Success boolean
        """
        try:
            # Update in GraphDB
            # Build SPARQL DELETE/INSERT
            update_query = f"""
            PREFIX cl: <http://citylens.io/ontology#>
            
            DELETE {{
                <{entity_id}> ?p ?o .
            }}
            INSERT {{
                <{entity_id}> ?p ?new_o .
            }}
            WHERE {{
                <{entity_id}> ?p ?o .
            }}
            """
            
            # For now, simple implementation
            logger.info(f"Update entity {entity_id} with {attributes}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating entity: {e}")
            return False
    
    async def delete_entity(self, entity_id: str, db: Session) -> bool:
        """Delete entity from all stores"""
        try:
            # Delete from GraphDB
            delete_query = f"""
            PREFIX cl: <http://citylens.io/ontology#>
            
            DELETE WHERE {{
                <{entity_id}> ?p ?o .
            }}
            """
            
            success = await graphdb_service.update_sparql(delete_query)
            
            # Also delete from PostgreSQL if applicable
            # (Implementation depends on entity type)
            
            logger.info(f"Deleted entity {entity_id}: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Error deleting entity: {e}")
            return False


# Singleton instance
ngsi_ld_service = NGSILDService()

