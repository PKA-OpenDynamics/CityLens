# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
SOSA/SSN Service
Converts application data to SOSA/SSN format for semantic web
"""

from typing import Dict, Any, Optional
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime
import logging

from .graphdb_service import graphdb_service

logger = logging.getLogger(__name__)

# Namespaces
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
CL = Namespace("http://citylens.io/ontology#")
GEO = Namespace("http://www.opengis.net/ont/geosparql#")


class SOSAService:
    """
    Service for converting CityLens data to SOSA/SSN format
    
    Key concept: Model everything as observations made by sensors
    - Traditional IoT sensors → sosa:Sensor
    - Citizens → cl:CitizenSensor (subclass of sosa:Sensor)
    - Reports → sosa:Observation
    """
    
    def __init__(self):
        self.graph = Graph()
        self.graph.bind("sosa", SOSA)
        self.graph.bind("ssn", SSN)
        self.graph.bind("cl", CL)
        self.graph.bind("geo", GEO)
        
        logger.info("SOSA Service initialized")
    
    async def citizen_report_to_sosa(self, report: Dict[str, Any]) -> bool:
        """
        Convert citizen report to SOSA Observation
        
        This is the KEY INNOVATION: Citizens as Sensors
        
        Args:
            report: Report dict from PostgreSQL
                {
                    "id": 123,
                    "user_id": 456,
                    "category": "infrastructure",
                    "description": "Road damage",
                    "location": {"lat": 21.0285, "lon": 105.8542},
                    "created_at": "2025-11-25T14:30:00Z",
                    "related_street_id": 789
                }
        
        Returns:
            Success boolean
        """
        try:
            g = Graph()
            g.bind("sosa", SOSA)
            g.bind("cl", CL)
            g.bind("geo", GEO)
            
            # URIs
            sensor_uri = URIRef(f"http://citylens.io/sensor/citizen_{report['user_id']}")
            obs_uri = URIRef(f"http://citylens.io/observation/report_{report['id']}")
            user_uri = URIRef(f"http://citylens.io/user/{report['user_id']}")
            
            # Feature of Interest (what is being observed)
            if report.get('related_street_id'):
                foi_uri = URIRef(f"http://citylens.io/street/{report['related_street_id']}")
            else:
                foi_uri = URIRef(f"http://citylens.io/location/{report['id']}")
            
            # Observable Property (what characteristic is observed)
            observable_map = {
                "infrastructure": CL.RoadCondition,
                "environment": CL.WasteCondition,
                "traffic": CL.TrafficCongestion,
                "security": CL.PublicSafetyIssue,
            }
            observable_prop = observable_map.get(report['category'], CL.RoadCondition)
            
            # ====================
            # 1. SENSOR (Citizen as Sensor)
            # ====================
            g.add((sensor_uri, RDF.type, CL.CitizenSensor))
            g.add((sensor_uri, RDF.type, SOSA.Sensor))
            g.add((sensor_uri, RDFS.label, Literal(f"Citizen Sensor {report['user_id']}")))
            g.add((sensor_uri, CL.belongsToUser, user_uri))
            g.add((sensor_uri, SOSA.observes, observable_prop))
            
            # ====================
            # 2. OBSERVATION (The report itself)
            # ====================
            g.add((obs_uri, RDF.type, CL.CitizenReport))
            g.add((obs_uri, RDF.type, SOSA.Observation))
            g.add((obs_uri, RDFS.label, Literal(f"Citizen Report {report['id']}")))
            
            # Who observed
            g.add((obs_uri, SOSA.madeBySensor, sensor_uri))
            
            # What was observed
            g.add((obs_uri, SOSA.hasFeatureOfInterest, foi_uri))
            g.add((obs_uri, SOSA.observedProperty, observable_prop))
            
            # Result (description)
            g.add((obs_uri, SOSA.hasSimpleResult, 
                  Literal(report['description'], lang='vi')))
            
            # When
            result_time = report.get('created_at')
            if isinstance(result_time, str):
                result_time = datetime.fromisoformat(result_time.replace('Z', '+00:00'))
            g.add((obs_uri, SOSA.resultTime, 
                  Literal(result_time, datatype=XSD.dateTime)))
            
            # ====================
            # 3. GEOMETRY
            # ====================
            location = report.get('location', {})
            if location:
                lon = location.get('lon')
                lat = location.get('lat')
                if lon and lat:
                    wkt = f"POINT({lon} {lat})"
                    g.add((obs_uri, GEO.hasGeometry, 
                          Literal(wkt, datatype=GEO.wktLiteral)))
            
            # ====================
            # 4. CITYLENS-SPECIFIC PROPERTIES
            # ====================
            g.add((obs_uri, CL.hasCategory, Literal(report['category'])))
            
            if report.get('severity'):
                g.add((obs_uri, CL.hasSeverity, Literal(report['severity'])))
            
            if report.get('status'):
                g.add((obs_uri, CL.hasStatus, Literal(report['status'])))
            
            if report.get('confidence_score'):
                g.add((obs_uri, CL.hasConfidenceScore, 
                      Literal(report['confidence_score'], datatype=XSD.float)))
            
            # Media evidence
            if report.get('images'):
                for img_url in report['images']:
                    g.add((obs_uri, CL.hasMediaEvidence, URIRef(img_url)))
            
            # ====================
            # 5. RELATIONSHIPS
            # ====================
            if report.get('district_id'):
                district_uri = URIRef(f"http://citylens.io/district/{report['district_id']}")
                g.add((obs_uri, CL.locatedIn, district_uri))
            
            if report.get('related_street_id'):
                street_uri = URIRef(f"http://citylens.io/street/{report['related_street_id']}")
                g.add((obs_uri, CL.concernsStreet, street_uri))
            
            # ====================
            # 6. INSERT INTO GRAPHDB
            # ====================
            turtle_data = g.serialize(format="turtle")
            success = await graphdb_service.insert_rdf_triples(turtle_data, format="turtle")
            
            if success:
                logger.info(f"Successfully converted report {report['id']} to SOSA and stored in GraphDB")
            else:
                logger.error(f"Failed to store SOSA observation for report {report['id']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error converting citizen report to SOSA: {e}")
            return False
    
    async def aqi_data_to_sosa(self, aqi_data: Dict[str, Any]) -> bool:
        """
        Convert AQI measurement to SOSA Observation
        
        Args:
            aqi_data: AQI data dict
                {
                    "id": 1,
                    "district_id": 1,
                    "value": 85,
                    "pm25": 45.2,
                    "measured_at": "2025-11-25T10:00:00Z"
                }
        
        Returns:
            Success boolean
        """
        try:
            g = Graph()
            g.bind("sosa", SOSA)
            g.bind("cl", CL)
            
            # URIs
            sensor_uri = URIRef(f"http://citylens.io/sensor/aqi_{aqi_data['district_id']}")
            obs_uri = URIRef(f"http://citylens.io/observation/aqi_{aqi_data['id']}")
            district_uri = URIRef(f"http://citylens.io/district/{aqi_data['district_id']}")
            
            # Sensor
            g.add((sensor_uri, RDF.type, CL.AQISensor))
            g.add((sensor_uri, RDF.type, SOSA.Sensor))
            g.add((sensor_uri, SOSA.observes, CL.AirQualityIndex))
            
            # Observation
            g.add((obs_uri, RDF.type, CL.AQIObservation))
            g.add((obs_uri, RDF.type, SOSA.Observation))
            g.add((obs_uri, SOSA.madeBySensor, sensor_uri))
            g.add((obs_uri, SOSA.hasFeatureOfInterest, district_uri))
            g.add((obs_uri, SOSA.observedProperty, CL.AirQualityIndex))
            g.add((obs_uri, SOSA.hasSimpleResult, 
                  Literal(aqi_data['value'], datatype=XSD.integer)))
            
            # Time
            measured_at = aqi_data.get('measured_at')
            if isinstance(measured_at, str):
                measured_at = datetime.fromisoformat(measured_at.replace('Z', '+00:00'))
            g.add((obs_uri, SOSA.resultTime, 
                  Literal(measured_at, datatype=XSD.dateTime)))
            
            # Additional measurements
            if aqi_data.get('pm25'):
                pm25_obs = URIRef(f"{obs_uri}_pm25")
                g.add((pm25_obs, RDF.type, SOSA.Observation))
                g.add((pm25_obs, SOSA.madeBySensor, sensor_uri))
                g.add((pm25_obs, SOSA.observedProperty, CL.PM25Concentration))
                g.add((pm25_obs, SOSA.hasSimpleResult, 
                      Literal(aqi_data['pm25'], datatype=XSD.float)))
            
            # Unit
            g.add((obs_uri, CL.hasUnit, Literal("AQI")))
            
            # Insert into GraphDB
            turtle_data = g.serialize(format="turtle")
            return await graphdb_service.insert_rdf_triples(turtle_data, format="turtle")
            
        except Exception as e:
            logger.error(f"Error converting AQI data to SOSA: {e}")
            return False
    
    async def traffic_data_to_sosa(self, traffic_data: Dict[str, Any]) -> bool:
        """
        Convert traffic observation to SOSA
        
        Args:
            traffic_data: Traffic data dict
        
        Returns:
            Success boolean
        """
        try:
            g = Graph()
            g.bind("sosa", SOSA)
            g.bind("cl", CL)
            
            sensor_uri = URIRef(f"http://citylens.io/sensor/traffic_{traffic_data['street_id']}")
            obs_uri = URIRef(f"http://citylens.io/observation/traffic_{traffic_data['id']}")
            street_uri = URIRef(f"http://citylens.io/street/{traffic_data['street_id']}")
            
            # Sensor
            g.add((sensor_uri, RDF.type, CL.TrafficFlowSensor))
            g.add((sensor_uri, SOSA.observes, CL.TrafficFlow))
            
            # Observation
            g.add((obs_uri, RDF.type, CL.TrafficObservation))
            g.add((obs_uri, SOSA.madeBySensor, sensor_uri))
            g.add((obs_uri, SOSA.hasFeatureOfInterest, street_uri))
            g.add((obs_uri, SOSA.observedProperty, CL.TrafficFlow))
            
            # Result
            if traffic_data.get('intensity'):
                g.add((obs_uri, SOSA.hasSimpleResult, 
                      Literal(f"{traffic_data['intensity']} vehicles/hour")))
            
            # Insert
            turtle_data = g.serialize(format="turtle")
            return await graphdb_service.insert_rdf_triples(turtle_data, format="turtle")
            
        except Exception as e:
            logger.error(f"Error converting traffic data to SOSA: {e}")
            return False
    
    async def parking_data_to_sosa(self, parking_data: Dict[str, Any]) -> bool:
        """
        Convert parking occupancy to SOSA
        
        Args:
            parking_data: Parking data dict
        
        Returns:
            Success boolean
        """
        try:
            g = Graph()
            g.bind("sosa", SOSA)
            g.bind("cl", CL)
            
            sensor_uri = URIRef(f"http://citylens.io/sensor/parking_{parking_data['facility_id']}")
            obs_uri = URIRef(f"http://citylens.io/observation/parking_{parking_data['id']}")
            facility_uri = URIRef(f"http://citylens.io/parking/{parking_data['facility_id']}")
            
            # Sensor
            g.add((sensor_uri, RDF.type, CL.SmartParkingSensor))
            g.add((sensor_uri, SOSA.observes, CL.ParkingOccupancy))
            
            # Observation
            g.add((obs_uri, RDF.type, CL.ParkingObservation))
            g.add((obs_uri, SOSA.madeBySensor, sensor_uri))
            g.add((obs_uri, SOSA.hasFeatureOfInterest, facility_uri))
            g.add((obs_uri, SOSA.observedProperty, CL.ParkingOccupancy))
            
            # Result
            available = parking_data.get('available_spots', 0)
            total = parking_data.get('total_spots', 0)
            occupancy = (total - available) / total if total > 0 else 0
            
            g.add((obs_uri, SOSA.hasSimpleResult, 
                  Literal(occupancy, datatype=XSD.float)))
            
            # Insert
            turtle_data = g.serialize(format="turtle")
            return await graphdb_service.insert_rdf_triples(turtle_data, format="turtle")
            
        except Exception as e:
            logger.error(f"Error converting parking data to SOSA: {e}")
            return False


# Singleton instance
sosa_service = SOSAService()

