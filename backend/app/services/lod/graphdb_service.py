# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
GraphDB Service
Handles RDF/SPARQL operations with Apache Jena Fuseki
"""

from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD
from SPARQLWrapper import SPARQLWrapper, POST, GET, JSON, DIGEST
import httpx
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

# Namespaces
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
CL = Namespace("http://citylens.io/ontology#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
NGSI_LD = Namespace("https://uri.etsi.org/ngsi-ld/")


class GraphDBService:
    """Service for interacting with GraphDB (Apache Jena Fuseki)"""
    
    def __init__(self):
        self.base_url = settings.GRAPHDB_URL
        self.repository = settings.GRAPHDB_REPOSITORY or "citylens"
        self.endpoint = f"{self.base_url}/{self.repository}"
        
        # SPARQL endpoints
        self.query_endpoint = f"{self.endpoint}/sparql"
        self.update_endpoint = f"{self.endpoint}/update"
        self.data_endpoint = f"{self.endpoint}/data"
        
        # Initialize SPARQL wrapper
        self.sparql = SPARQLWrapper(self.query_endpoint)
        self.sparql.setReturnFormat(JSON)
        
        # Initialize graph for building RDF
        self.graph = Graph()
        self.graph.bind("sosa", SOSA)
        self.graph.bind("ssn", SSN)
        self.graph.bind("cl", CL)
        self.graph.bind("geo", GEO)
        self.graph.bind("ngsi-ld", NGSI_LD)
        
        logger.info(f"GraphDB service initialized: {self.endpoint}")
    
    async def insert_rdf_triples(self, triples: str, format: str = "turtle") -> bool:
        """
        Insert RDF triples into GraphDB
        
        Args:
            triples: RDF data as string
            format: RDF format (turtle, n3, rdfxml, etc.)
        
        Returns:
            Success boolean
        """
        try:
            headers = {
                "Content-Type": f"text/{format}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.data_endpoint,
                    content=triples,
                    headers=headers,
                    timeout=30.0
                )
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"Successfully inserted RDF triples into GraphDB")
                return True
            else:
                logger.error(f"Failed to insert RDF: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error inserting RDF triples: {e}")
            return False
    
    async def query_sparql(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute SPARQL SELECT query
        
        Args:
            query: SPARQL query string
        
        Returns:
            List of result bindings
        """
        try:
            self.sparql.setQuery(query)
            self.sparql.setMethod(GET)
            results = self.sparql.query().convert()
            
            # Extract bindings
            bindings = results.get("results", {}).get("bindings", [])
            
            # Simplify results
            simplified = []
            for binding in bindings:
                row = {}
                for key, value in binding.items():
                    row[key] = value.get("value")
                simplified.append(row)
            
            logger.info(f"SPARQL query returned {len(simplified)} results")
            return simplified
            
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {e}")
            return []
    
    async def update_sparql(self, update_query: str) -> bool:
        """
        Execute SPARQL UPDATE query (INSERT, DELETE, etc.)
        
        Args:
            update_query: SPARQL UPDATE query
        
        Returns:
            Success boolean
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.update_endpoint,
                    data={"update": update_query},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=30.0
                )
            
            if response.status_code in [200, 201, 204]:
                logger.info("SPARQL UPDATE executed successfully")
                return True
            else:
                logger.error(f"SPARQL UPDATE failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing SPARQL UPDATE: {e}")
            return False
    
    async def insert_ngsi_ld_entity(self, entity: Dict[str, Any]) -> bool:
        """
        Insert NGSI-LD entity as RDF triples
        
        Args:
            entity: NGSI-LD entity dict
        
        Returns:
            Success boolean
        """
        try:
            # Convert NGSI-LD to RDF triples
            entity_uri = URIRef(entity["id"])
            entity_type = URIRef(f"http://citylens.io/ontology#{entity['type']}")
            
            g = Graph()
            g.bind("cl", CL)
            g.bind("ngsi-ld", NGSI_LD)
            
            # Type
            g.add((entity_uri, RDF.type, entity_type))
            
            # Process attributes
            for key, value in entity.items():
                if key in ["id", "type", "@context", "createdAt", "modifiedAt"]:
                    continue
                
                if isinstance(value, dict):
                    attr_type = value.get("type")
                    attr_value = value.get("value")
                    
                    if attr_type == "Property":
                        # Add property
                        pred = URIRef(f"http://citylens.io/ontology#{key}")
                        
                        # Convert value to appropriate literal
                        if isinstance(attr_value, bool):
                            obj = Literal(attr_value, datatype=XSD.boolean)
                        elif isinstance(attr_value, int):
                            obj = Literal(attr_value, datatype=XSD.integer)
                        elif isinstance(attr_value, float):
                            obj = Literal(attr_value, datatype=XSD.float)
                        elif isinstance(attr_value, str):
                            obj = Literal(attr_value)
                        else:
                            obj = Literal(str(attr_value))
                        
                        g.add((entity_uri, pred, obj))
                    
                    elif attr_type == "GeoProperty":
                        # Add geometry
                        coords = attr_value.get("coordinates", [])
                        if attr_value.get("type") == "Point":
                            wkt = f"POINT({coords[0]} {coords[1]})"
                            g.add((entity_uri, GEO.hasGeometry, Literal(wkt, datatype=GEO.wktLiteral)))
                    
                    elif attr_type == "Relationship":
                        # Add relationship
                        pred = URIRef(f"http://citylens.io/ontology#{key}")
                        obj = URIRef(value.get("object"))
                        g.add((entity_uri, pred, obj))
            
            # Serialize to Turtle
            turtle_data = g.serialize(format="turtle")
            
            # Insert into GraphDB
            return await self.insert_rdf_triples(turtle_data, format="turtle")
            
        except Exception as e:
            logger.error(f"Error inserting NGSI-LD entity: {e}")
            return False
    
    async def find_related_reports(
        self,
        report_id: int,
        max_distance_m: float = 1000,
        same_category: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find reports related to given report
        Uses SPARQL geo-spatial queries
        
        Args:
            report_id: Report ID
            max_distance_m: Maximum distance in meters
            same_category: Filter by same category
        
        Returns:
            List of related reports with distance
        """
        query = f"""
        PREFIX cl: <http://citylens.io/ontology#>
        PREFIX geo: <http://www.opengis.net/ont/geosparql#>
        PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
        PREFIX sosa: <http://www.w3.org/ns/sosa/>
        
        SELECT ?report ?category ?status ?distance
        WHERE {{
            # Original report
            <http://citylens.io/observation/report_{report_id}> 
                cl:hasCategory ?cat1 ;
                geo:hasGeometry ?geom1 .
            
            # Find related reports
            ?report a cl:CitizenReport ;
                cl:hasCategory ?category ;
                cl:hasStatus ?status ;
                geo:hasGeometry ?geom2 .
            
            # Same category filter (optional)
            {"FILTER(?category = ?cat1)" if same_category else ""}
            
            # Exclude self
            FILTER(?report != <http://citylens.io/observation/report_{report_id}>)
            
            # Calculate distance
            BIND(geof:distance(?geom1, ?geom2, <http://www.opengis.net/def/uom/OGC/1.0/metre>) AS ?distance)
            
            # Distance filter
            FILTER(?distance < {max_distance_m})
        }}
        ORDER BY ?distance
        LIMIT 10
        """
        
        return await self.query_sparql(query)
    
    async def get_district_statistics(self, district_id: int) -> Dict[str, Any]:
        """
        Get aggregated statistics for a district
        
        Args:
            district_id: District ID
        
        Returns:
            Statistics dict
        """
        query = f"""
        PREFIX cl: <http://citylens.io/ontology#>
        
        SELECT 
            (COUNT(?report) AS ?total_reports)
            (COUNT(?pending) AS ?pending_reports)
            (COUNT(?resolved) AS ?resolved_reports)
        WHERE {{
            ?report a cl:CitizenReport ;
                cl:locatedIn <http://citylens.io/district/{district_id}> ;
                cl:hasStatus ?status .
            
            OPTIONAL {{ ?report cl:hasStatus "pending" . BIND(?report AS ?pending) }}
            OPTIONAL {{ ?report cl:hasStatus "resolved" . BIND(?report AS ?resolved) }}
        }}
        """
        
        results = await self.query_sparql(query)
        return results[0] if results else {}
    
    async def export_entity_as_rdf(self, entity_id: str, format: str = "turtle") -> str:
        """
        Export entity and its relationships as RDF
        
        Args:
            entity_id: Entity URI
            format: Output format (turtle, rdfxml, n3)
        
        Returns:
            RDF data as string
        """
        query = f"""
        CONSTRUCT {{
            <{entity_id}> ?p ?o .
            ?o ?p2 ?o2 .
        }}
        WHERE {{
            <{entity_id}> ?p ?o .
            OPTIONAL {{ ?o ?p2 ?o2 }}
        }}
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setMethod(GET)
            self.sparql.setReturnFormat(format.upper())
            results = self.sparql.query().convert()
            
            return results.decode('utf-8') if isinstance(results, bytes) else results
            
        except Exception as e:
            logger.error(f"Error exporting entity as RDF: {e}")
            return ""


# Singleton instance
graphdb_service = GraphDBService()

