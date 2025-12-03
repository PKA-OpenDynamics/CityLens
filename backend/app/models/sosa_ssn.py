"""
SOSA/SSN Ontology Models - W3C Standard Compliant

Implements:
- SOSA (Sensor, Observation, Sample, and Actuator) Core Ontology
- SSN (Semantic Sensor Network) Extension

References:
- W3C SOSA/SSN: https://www.w3.org/TR/vocab-ssn/
- SOSA Core: https://www.w3.org/ns/sosa/
- SSN Extension: https://www.w3.org/ns/ssn/

Author: CityLens Development Team
License: GPL-3.0
Date: 2025-12-03
"""

from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.ngsi_ld import Entity, Property, Relationship, GeoProperty


# ============================================================================
# SOSA CORE CLASSES
# ============================================================================

class Sensor(Entity):
    """
    SOSA Sensor - A device, agent, or software that makes observations.
    
    A sensor is a device that detects and responds to events or changes in 
    the physical environment and provides a corresponding output.
    
    SOSA Properties:
    - observes: The observable properties that the sensor can observe
    - isHostedBy: The platform that hosts this sensor
    - hasSubSystem: Sub-sensors or components
    
    SSN Extension Properties:
    - hasDeployment: Deployment information
    - inDeployment: Current deployment
    - detects: Stimulus that the sensor can detect
    
    Example:
        Air Quality Sensor observes PM2.5, PM10, NO2, SO2, CO, O3
        Weather Station observes temperature, humidity, pressure, windSpeed
        Traffic Camera observes vehicleCount, averageSpeed, congestion
    """
    type: Literal["Sensor"] = "Sensor"
    
    # SOSA Core Properties (Required)
    observes: Property = Field(
        ...,
        description="List of observable properties that this sensor can measure"
    )
    
    # Identification & Description
    name: Property = Field(..., description="Human-readable name of the sensor")
    description: Optional[Property] = Field(None, description="Detailed description")
    
    # Location (GeoProperty)
    location: Optional[GeoProperty] = Field(None, description="Geographic location of sensor")
    
    # Technical Specifications
    manufacturer: Optional[Property] = Field(None, description="Manufacturer name")
    model: Optional[Property] = Field(None, description="Model number/name")
    serialNumber: Optional[Property] = Field(None, description="Serial number")
    firmwareVersion: Optional[Property] = Field(None, description="Firmware version")
    
    # Operational Status
    status: Property = Field(
        default=Property(type="Property", value="active"),
        description="Operational status: active, inactive, maintenance, error"
    )
    
    # Relationships (SOSA/SSN)
    isHostedBy: Optional[Relationship] = Field(
        None, 
        description="Platform that hosts this sensor (e.g., weather station, monitoring station)"
    )
    hasSubSystem: Optional[Relationship] = Field(
        None,
        description="Sub-sensors or components (e.g., PM2.5 sensor inside AQI station)"
    )
    hasDeployment: Optional[Relationship] = Field(
        None,
        description="Deployment entity describing how/where/when sensor is deployed"
    )
    
    # Measurement Capabilities
    measurementRange: Optional[Property] = Field(
        None,
        description="Range of values the sensor can measure (e.g., {'min': 0, 'max': 500} for AQI)"
    )
    measurementAccuracy: Optional[Property] = Field(
        None,
        description="Accuracy/precision of measurements (e.g., ±0.5°C)"
    )
    measurementFrequency: Optional[Property] = Field(
        None,
        description="How often sensor takes measurements (e.g., 'every 15 minutes')"
    )
    
    # Temporal Properties
    dateInstalled: Optional[Property] = Field(None, description="Installation date")
    dateCalibrated: Optional[Property] = Field(None, description="Last calibration date")
    dateFirstUsed: Optional[Property] = Field(None, description="First operational date")
    
    # Contact & Maintenance
    owner: Optional[Property] = Field(None, description="Organization/person owning the sensor")
    contactPoint: Optional[Property] = Field(None, description="Contact information")


class ObservableProperty(Entity):
    """
    SOSA Observable Property - A property that can be observed by a sensor.
    
    Represents the phenomenon being measured (e.g., temperature, PM2.5 concentration).
    
    Examples:
    - AirTemperature (measured in Celsius)
    - PM2.5Concentration (measured in µg/m³)
    - RelativeHumidity (measured in %)
    - TrafficFlow (measured in vehicles/hour)
    
    Properties:
    - label: Human-readable name
    - description: What this property represents
    - unitCode: Standard unit of measurement (UN/CEFACT codes)
    - domain: Domain of application (Environment, Transportation, Weather)
    """
    type: Literal["ObservableProperty"] = "ObservableProperty"
    
    label: Property = Field(..., description="Human-readable label (e.g., 'PM2.5 Concentration')")
    description: Property = Field(..., description="What this property measures")
    unitCode: Property = Field(
        ...,
        description="UN/CEFACT unit code (e.g., 'CEL' for Celsius, 'GQ' for µg/m³)"
    )
    domain: Property = Field(
        ...,
        description="Application domain: Environment, Transportation, Weather, etc."
    )
    
    # Optional metadata
    standardDefinition: Optional[Property] = Field(
        None,
        description="Link to standard definition (e.g., WHO air quality standards)"
    )
    alternateLabels: Optional[Property] = Field(
        None,
        description="Alternative names (e.g., ['Fine Particulate Matter', 'Particulate Matter 2.5'])"
    )


class Observation(Entity):
    """
    SOSA Observation - Result of carrying out an observing procedure by a sensor.
    
    An observation links:
    - A sensor (madeBySensor)
    - An observable property (observedProperty)
    - A feature of interest (hasFeatureOfInterest) - what is being observed
    - A result (hasResult) - the measured value
    - A time (resultTime, phenomenonTime)
    
    This is the CENTRAL entity in SOSA ontology connecting all pieces.
    
    SOSA Properties:
    - madeBySensor: The sensor that made this observation
    - observedProperty: What property was observed
    - hasFeatureOfInterest: The real-world entity being observed
    - hasResult: The measured value
    - resultTime: When the result was generated
    - phenomenonTime: When the phenomenon occurred
    - usedProcedure: The procedure/method used
    
    Example:
        Observation {
          madeBySensor: Sensor:AQI:Hanoi:Station01
          observedProperty: ObservableProperty:PM2.5
          hasFeatureOfInterest: Location:Hanoi:HoanKiem
          hasResult: 25.5 µg/m³
          resultTime: 2025-12-03T10:00:00Z
        }
    """
    type: Literal["Observation"] = "Observation"
    
    # SOSA Core Relationships (Required)
    madeBySensor: Relationship = Field(
        ...,
        description="The sensor that made this observation (links to Sensor entity)"
    )
    observedProperty: Relationship = Field(
        ...,
        description="The property that was observed (links to ObservableProperty entity)"
    )
    hasFeatureOfInterest: Relationship = Field(
        ...,
        description="The entity being observed (e.g., location, road segment, building)"
    )
    
    # Result Properties (Required)
    hasResult: Property = Field(
        ...,
        description="The measured value with unitCode"
    )
    
    # Temporal Properties (Required)
    resultTime: Property = Field(
        ...,
        description="When the observation result was generated"
    )
    phenomenonTime: Optional[Property] = Field(
        None,
        description="The time of the phenomenon being observed (may differ from resultTime)"
    )
    
    # Optional SOSA Properties
    usedProcedure: Optional[Relationship] = Field(
        None,
        description="The procedure/method used to make the observation"
    )
    madeBySampler: Optional[Relationship] = Field(
        None,
        description="Sampler used (if observation involves sampling)"
    )
    
    # Quality & Validation
    qualityFlag: Optional[Property] = Field(
        None,
        description="Data quality indicator: good, suspect, bad, missing"
    )
    validationStatus: Optional[Property] = Field(
        None,
        description="Validation status: validated, pending, rejected"
    )
    
    # Location (may differ from sensor location)
    location: Optional[GeoProperty] = Field(
        None,
        description="Where the observation was made (may be mobile sensor)"
    )


class Platform(Entity):
    """
    SSN Platform - A structure that hosts one or more sensors.
    
    A platform is an entity that hosts sensors and provides infrastructure
    for sensor operations (power, communication, physical support).
    
    Examples:
    - Weather Station (hosts temperature, humidity, pressure sensors)
    - Air Quality Monitoring Station (hosts PM2.5, NO2, SO2 sensors)
    - Traffic Monitoring Tower (hosts traffic cameras, speed sensors)
    - IoT Gateway (hosts multiple environmental sensors)
    - Satellite (hosts remote sensing instruments)
    
    SSN Properties:
    - hosts: List of sensors hosted by this platform
    - inDeployment: Deployment information
    """
    type: Literal["Platform"] = "Platform"
    
    # Identification
    name: Property = Field(..., description="Platform name")
    description: Optional[Property] = Field(None, description="Platform description")
    
    # Location
    location: GeoProperty = Field(..., description="Platform location")
    
    # Relationships
    hosts: Relationship = Field(
        ...,
        description="Sensors hosted by this platform (array of sensor URNs)"
    )
    
    # Technical Details
    platformType: Property = Field(
        ...,
        description="Type: weather_station, aqi_station, traffic_tower, iot_gateway, satellite"
    )
    
    # Operational
    status: Property = Field(
        default=Property(type="Property", value="operational"),
        description="Status: operational, maintenance, offline"
    )
    owner: Optional[Property] = Field(None, description="Owner organization")
    operator: Optional[Property] = Field(None, description="Operating organization")
    
    # Infrastructure
    powerSource: Optional[Property] = Field(
        None,
        description="Power source: grid, solar, battery, hybrid"
    )
    connectivity: Optional[Property] = Field(
        None,
        description="Communication method: 4G, WiFi, LoRaWAN, satellite"
    )
    
    # Temporal
    dateInstalled: Optional[Property] = Field(None, description="Installation date")
    dateDecommissioned: Optional[Property] = Field(None, description="Decommission date")


class FeatureOfInterest(Entity):
    """
    SOSA Feature of Interest - The real-world entity being observed.
    
    A feature of interest is the thing whose property is being observed.
    It represents the real-world entity or location that is the subject
    of observations.
    
    Examples:
    - A specific location (e.g., Hoan Kiem District)
    - A road segment (e.g., Nguyen Trai Street)
    - A building (e.g., Ba Dinh Square)
    - A water body (e.g., West Lake)
    - An administrative area (e.g., Hanoi City)
    
    Properties:
    - name: Name of the feature
    - type: Type of feature (location, road, building, area, water_body)
    - location: Geographic location
    - hasSample: Samples taken from this feature
    """
    type: Literal["FeatureOfInterest"] = "FeatureOfInterest"
    
    name: Property = Field(..., description="Name of the feature")
    description: Optional[Property] = Field(None, description="Description")
    
    featureType: Property = Field(
        ...,
        description="Type: location, road_segment, building, administrative_area, water_body, air_volume"
    )
    
    location: Optional[GeoProperty] = Field(
        None,
        description="Geographic location (Point, Polygon, LineString)"
    )
    
    # Relationships
    hasSample: Optional[Relationship] = Field(
        None,
        description="Samples taken from this feature"
    )
    
    # Metadata
    administrativeArea: Optional[Property] = Field(
        None,
        description="Administrative area containing this feature"
    )


class Procedure(Entity):
    """
    SOSA Procedure - A method, algorithm, or process for making observations.
    
    Describes how observations are made, including:
    - Measurement methodology
    - Calibration procedures
    - Quality control steps
    - Data processing algorithms
    
    Examples:
    - "EPA Air Quality Measurement Protocol"
    - "WMO Weather Observation Standards"
    - "Traffic Flow Calculation Algorithm"
    """
    type: Literal["Procedure"] = "Procedure"
    
    name: Property = Field(..., description="Procedure name")
    description: Property = Field(..., description="Detailed procedure description")
    
    # Standards & References
    standardReference: Optional[Property] = Field(
        None,
        description="Reference to standard (e.g., ISO, EPA, WMO)"
    )
    version: Optional[Property] = Field(None, description="Procedure version")
    
    # Documentation
    documentation: Optional[Property] = Field(
        None,
        description="URL to full documentation"
    )


# ============================================================================
# HELPER FUNCTIONS TO CREATE SOSA/SSN ENTITIES
# ============================================================================

def create_sensor_entity(
    sensor_id: str,
    name: str,
    observes: List[str],
    location: Dict[str, Any],
    platform_id: Optional[str] = None,
    manufacturer: Optional[str] = None,
    status: str = "active",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a SOSA/SSN compliant Sensor entity.
    
    Args:
        sensor_id: URN format (e.g., urn:ngsi-ld:Sensor:AQI:Hanoi:Station01)
        name: Human-readable name
        observes: List of observable property names
        location: GeoJSON location
        platform_id: URN of host platform (optional)
        manufacturer: Manufacturer name (optional)
        status: Sensor status (default: active)
        **kwargs: Additional properties
    
    Returns:
        NGSI-LD compliant Sensor entity dict
    """
    entity = {
        "id": sensor_id,
        "type": "Sensor",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "http://www.w3.org/ns/sosa/",
            "http://www.w3.org/ns/ssn/"
        ],
        "observes": {
            "type": "Property",
            "value": observes
        },
        "name": {
            "type": "Property",
            "value": name
        },
        "location": {
            "type": "GeoProperty",
            "value": location
        },
        "status": {
            "type": "Property",
            "value": status
        }
    }
    
    if platform_id:
        entity["isHostedBy"] = {
            "type": "Relationship",
            "object": platform_id
        }
    
    if manufacturer:
        entity["manufacturer"] = {
            "type": "Property",
            "value": manufacturer
        }
    
    # Add any additional properties from kwargs
    for key, value in kwargs.items():
        if key not in entity:
            entity[key] = {
                "type": "Property",
                "value": value
            }
    
    return entity


def create_observation_entity(
    observation_id: str,
    sensor_id: str,
    observable_property_id: str,
    feature_of_interest_id: str,
    result_value: Any,
    result_time: str,
    unit_code: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a SOSA compliant Observation entity.
    
    Args:
        observation_id: URN (e.g., urn:ngsi-ld:Observation:PM25:Hanoi:1733234567)
        sensor_id: URN of sensor that made observation
        observable_property_id: URN of observable property
        feature_of_interest_id: URN of feature being observed
        result_value: Measured value
        result_time: ISO 8601 timestamp
        unit_code: UN/CEFACT unit code (optional)
        location: GeoJSON location (optional)
        **kwargs: Additional properties
    
    Returns:
        NGSI-LD compliant Observation entity dict
    """
    entity = {
        "id": observation_id,
        "type": "Observation",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "http://www.w3.org/ns/sosa/"
        ],
        "madeBySensor": {
            "type": "Relationship",
            "object": sensor_id
        },
        "observedProperty": {
            "type": "Relationship",
            "object": observable_property_id
        },
        "hasFeatureOfInterest": {
            "type": "Relationship",
            "object": feature_of_interest_id
        },
        "hasResult": {
            "type": "Property",
            "value": result_value
        },
        "resultTime": {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": result_time
            }
        }
    }
    
    if unit_code:
        entity["hasResult"]["unitCode"] = unit_code
    
    if location:
        entity["location"] = {
            "type": "GeoProperty",
            "value": location
        }
    
    # Add additional properties
    for key, value in kwargs.items():
        if key not in entity:
            entity[key] = {
                "type": "Property",
                "value": value
            }
    
    return entity


def create_platform_entity(
    platform_id: str,
    name: str,
    platform_type: str,
    location: Dict[str, Any],
    sensor_ids: List[str],
    **kwargs
) -> Dict[str, Any]:
    """
    Create an SSN Platform entity.
    
    Args:
        platform_id: URN (e.g., urn:ngsi-ld:Platform:AQI:Hanoi:Station01)
        name: Platform name
        platform_type: Type of platform (weather_station, aqi_station, etc.)
        location: GeoJSON location
        sensor_ids: List of sensor URNs hosted by this platform
        **kwargs: Additional properties
    
    Returns:
        NGSI-LD compliant Platform entity dict
    """
    entity = {
        "id": platform_id,
        "type": "Platform",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "http://www.w3.org/ns/ssn/"
        ],
        "name": {
            "type": "Property",
            "value": name
        },
        "platformType": {
            "type": "Property",
            "value": platform_type
        },
        "location": {
            "type": "GeoProperty",
            "value": location
        },
        "hosts": {
            "type": "Relationship",
            "object": sensor_ids
        },
        "status": {
            "type": "Property",
            "value": kwargs.get("status", "operational")
        }
    }
    
    # Add additional properties
    for key, value in kwargs.items():
        if key not in entity and key != "status":
            entity[key] = {
                "type": "Property",
                "value": value
            }
    
    return entity
