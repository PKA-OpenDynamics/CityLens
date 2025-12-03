#!/usr/bin/env python3
"""
Seed SOSA/SSN Sensors, Platforms, Observable Properties, and Features of Interest

This script creates the foundational SOSA/SSN infrastructure for CityLens:
1. Observable Properties (what can be measured)
2. Features of Interest (what is being observed)
3. Platforms (infrastructure hosting sensors)
4. Sensors (devices making observations)

This establishes the semantic sensor network for:
- Air Quality Monitoring (AQICN)
- Weather Monitoring (OpenWeatherMap)
- Traffic Monitoring (TomTom)

Author: CityLens Development Team
License: GPL-3.0
Date: 2025-12-03
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_db
from app.repositories.entity_repository import EntityRepository
from app.models.ngsi_ld import Entity
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# OBSERVABLE PROPERTIES - What can be measured
# ============================================================================

OBSERVABLE_PROPERTIES = [
    # Air Quality Properties
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:PM2.5",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "PM2.5 Concentration"},
        "description": {"type": "Property", "value": "Fine particulate matter concentration (particles ≤ 2.5 micrometers)"},
        "unitCode": {"type": "Property", "value": "GQ"},  # µg/m³
        "domain": {"type": "Property", "value": "Environment"},
        "standardDefinition": {"type": "Property", "value": "WHO Air Quality Guidelines"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:PM10",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "PM10 Concentration"},
        "description": {"type": "Property", "value": "Coarse particulate matter concentration (particles ≤ 10 micrometers)"},
        "unitCode": {"type": "Property", "value": "GQ"},
        "domain": {"type": "Property", "value": "Environment"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:NO2",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Nitrogen Dioxide Concentration"},
        "description": {"type": "Property", "value": "NO2 gas concentration in air"},
        "unitCode": {"type": "Property", "value": "GQ"},
        "domain": {"type": "Property", "value": "Environment"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:SO2",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Sulfur Dioxide Concentration"},
        "description": {"type": "Property", "value": "SO2 gas concentration in air"},
        "unitCode": {"type": "Property", "value": "GQ"},
        "domain": {"type": "Property", "value": "Environment"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:CO",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Carbon Monoxide Concentration"},
        "description": {"type": "Property", "value": "CO gas concentration in air"},
        "unitCode": {"type": "Property", "value": "GP"},  # mg/m³
        "domain": {"type": "Property", "value": "Environment"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:O3",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Ozone Concentration"},
        "description": {"type": "Property", "value": "O3 gas concentration in air"},
        "unitCode": {"type": "Property", "value": "GQ"},
        "domain": {"type": "Property", "value": "Environment"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:AirQuality:AQI",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Air Quality Index"},
        "description": {"type": "Property", "value": "Composite air quality index (0-500 scale)"},
        "unitCode": {"type": "Property", "value": "C62"},  # Dimensionless
        "domain": {"type": "Property", "value": "Environment"},
        "standardDefinition": {"type": "Property", "value": "EPA Air Quality Index"}
    },
    
    # Weather Properties
    {
        "id": "urn:ngsi-ld:ObservableProperty:Weather:Temperature",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Air Temperature"},
        "description": {"type": "Property", "value": "Ambient air temperature"},
        "unitCode": {"type": "Property", "value": "CEL"},  # Celsius
        "domain": {"type": "Property", "value": "Weather"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:Weather:Humidity",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Relative Humidity"},
        "description": {"type": "Property", "value": "Percentage of moisture in air relative to maximum"},
        "unitCode": {"type": "Property", "value": "P1"},  # Percentage
        "domain": {"type": "Property", "value": "Weather"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:Weather:Pressure",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Atmospheric Pressure"},
        "description": {"type": "Property", "value": "Barometric pressure at sea level"},
        "unitCode": {"type": "Property", "value": "A97"},  # hPa (hectopascal)
        "domain": {"type": "Property", "value": "Weather"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:Weather:WindSpeed",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Wind Speed"},
        "description": {"type": "Property", "value": "Horizontal wind speed"},
        "unitCode": {"type": "Property", "value": "MTS"},  # m/s
        "domain": {"type": "Property", "value": "Weather"}
    },
    
    # Traffic Properties
    {
        "id": "urn:ngsi-ld:ObservableProperty:Traffic:VehicleSpeed",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Average Vehicle Speed"},
        "description": {"type": "Property", "value": "Mean speed of vehicles on road segment"},
        "unitCode": {"type": "Property", "value": "KMH"},  # km/h
        "domain": {"type": "Property", "value": "Transportation"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:Traffic:CongestionLevel",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Traffic Congestion Level"},
        "description": {"type": "Property", "value": "Ratio of current to free-flow speed (0-1 scale)"},
        "unitCode": {"type": "Property", "value": "C62"},  # Dimensionless
        "domain": {"type": "Property", "value": "Transportation"}
    },
    {
        "id": "urn:ngsi-ld:ObservableProperty:Traffic:TravelTime",
        "type": "ObservableProperty",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "label": {"type": "Property", "value": "Travel Time"},
        "description": {"type": "Property", "value": "Time required to traverse road segment"},
        "unitCode": {"type": "Property", "value": "SEC"},  # Seconds
        "domain": {"type": "Property", "value": "Transportation"}
    }
]


# ============================================================================
# FEATURES OF INTEREST - What is being observed
# ============================================================================

FEATURES_OF_INTEREST = [
    # Locations in Hanoi
    {
        "id": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:City",
        "type": "FeatureOfInterest",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "name": {"type": "Property", "value": "Hanoi City"},
        "description": {"type": "Property", "value": "Capital city of Vietnam"},
        "featureType": {"type": "Property", "value": "administrative_area"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8542, 21.0285]  # City center
            }
        },
        "administrativeArea": {"type": "Property", "value": "Hanoi"}
    },
    {
        "id": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:HoanKiem",
        "type": "FeatureOfInterest",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "name": {"type": "Property", "value": "Hoan Kiem District"},
        "description": {"type": "Property", "value": "Central district of Hanoi"},
        "featureType": {"type": "Property", "value": "administrative_area"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8542, 21.0285]
            }
        },
        "administrativeArea": {"type": "Property", "value": "Hanoi"}
    },
    {
        "id": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:BaDinh",
        "type": "FeatureOfInterest",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "name": {"type": "Property", "value": "Ba Dinh District"},
        "description": {"type": "Property", "value": "Political and administrative center"},
        "featureType": {"type": "Property", "value": "administrative_area"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8342, 21.0368]
            }
        },
        "administrativeArea": {"type": "Property", "value": "Hanoi"}
    },
    # Air volumes (for air quality monitoring)
    {
        "id": "urn:ngsi-ld:FeatureOfInterest:AirVolume:Hanoi:Urban",
        "type": "FeatureOfInterest",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "name": {"type": "Property", "value": "Hanoi Urban Air Volume"},
        "description": {"type": "Property", "value": "Volume of air above urban Hanoi"},
        "featureType": {"type": "Property", "value": "air_volume"},
        "administrativeArea": {"type": "Property", "value": "Hanoi"}
    },
    # Road segments (for traffic monitoring)
    {
        "id": "urn:ngsi-ld:FeatureOfInterest:RoadSegment:Hanoi:HoanKiem",
        "type": "FeatureOfInterest",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/"],
        "name": {"type": "Property", "value": "Road Segment near Hoan Kiem Lake"},
        "description": {"type": "Property", "value": "Traffic monitoring zone in city center"},
        "featureType": {"type": "Property", "value": "road_segment"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8542, 21.0285]
            }
        }
    }
]


# ============================================================================
# PLATFORMS - Infrastructure hosting sensors
# ============================================================================

PLATFORMS = [
    # Air Quality Monitoring Station (AQICN)
    {
        "id": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station",
        "type": "Platform",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/ssn/"],
        "name": {"type": "Property", "value": "Hanoi Air Quality Monitoring Station (AQICN)"},
        "description": {"type": "Property", "value": "Government air quality monitoring station providing real-time AQI data"},
        "platformType": {"type": "Property", "value": "aqi_station"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8342, 21.0278]  # US Embassy Hanoi
            }
        },
        "hosts": {
            "type": "Relationship",
            "object": [
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM25",
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM10",
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_NO2",
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_SO2",
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_CO",
                "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_O3"
            ]
        },
        "status": {"type": "Property", "value": "operational"},
        "owner": {"type": "Property", "value": "World Air Quality Index Project"},
        "operator": {"type": "Property", "value": "AQICN"},
        "connectivity": {"type": "Property", "value": "Internet API"},
        "dateInstalled": {"type": "Property", "value": {"@type": "DateTime", "@value": "2015-01-01T00:00:00Z"}}
    },
    
    # Weather Station (OpenWeatherMap)
    {
        "id": "urn:ngsi-ld:Platform:Weather:Hanoi:OpenWeatherMap_Station",
        "type": "Platform",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/ssn/"],
        "name": {"type": "Property", "value": "Hanoi Weather Station (OpenWeatherMap)"},
        "description": {"type": "Property", "value": "Meteorological station providing real-time weather data"},
        "platformType": {"type": "Property", "value": "weather_station"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8542, 21.0285]  # Hanoi center
            }
        },
        "hosts": {
            "type": "Relationship",
            "object": [
                "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Temperature",
                "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Humidity",
                "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Pressure",
                "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_WindSpeed"
            ]
        },
        "status": {"type": "Property", "value": "operational"},
        "owner": {"type": "Property", "value": "OpenWeather Ltd."},
        "operator": {"type": "Property", "value": "OpenWeatherMap"},
        "connectivity": {"type": "Property", "value": "Internet API"}
    },
    
    # Traffic Monitoring Infrastructure (TomTom)
    {
        "id": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network",
        "type": "Platform",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/ssn/"],
        "name": {"type": "Property", "value": "Hanoi Traffic Monitoring Network (TomTom)"},
        "description": {"type": "Property", "value": "Distributed traffic monitoring system covering major roads"},
        "platformType": {"type": "Property", "value": "traffic_monitoring_network"},
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [105.8542, 21.0285]
            }
        },
        "hosts": {
            "type": "Relationship",
            "object": [
                "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_HoanKiem",
                "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_BaDinh",
                "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_MyDinh",
                "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_CauGiay",
                "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_LongBien"
            ]
        },
        "status": {"type": "Property", "value": "operational"},
        "owner": {"type": "Property", "value": "TomTom International BV"},
        "operator": {"type": "Property", "value": "TomTom Traffic"},
        "connectivity": {"type": "Property", "value": "Internet API"}
    }
]


# ============================================================================
# SENSORS - Devices making observations
# ============================================================================

SENSORS = [
    # ========== AIR QUALITY SENSORS (AQICN) ==========
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM25",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["PM2.5"]},
        "name": {"type": "Property", "value": "PM2.5 Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Fine particulate matter sensor measuring particles ≤ 2.5µm"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "manufacturer": {"type": "Property", "value": "MetOne Instruments"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"},
        "measurementAccuracy": {"type": "Property", "value": "±5 µg/m³"},
        "dateInstalled": {"type": "Property", "value": {"@type": "DateTime", "@value": "2015-01-01T00:00:00Z"}}
    },
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM10",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["PM10"]},
        "name": {"type": "Property", "value": "PM10 Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Coarse particulate matter sensor measuring particles ≤ 10µm"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "manufacturer": {"type": "Property", "value": "MetOne Instruments"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_NO2",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["NO2"]},
        "name": {"type": "Property", "value": "NO2 Gas Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Nitrogen dioxide gas concentration sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_SO2",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["SO2"]},
        "name": {"type": "Property", "value": "SO2 Gas Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Sulfur dioxide gas concentration sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_CO",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["CO"]},
        "name": {"type": "Property", "value": "CO Gas Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Carbon monoxide gas concentration sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_O3",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["O3"]},
        "name": {"type": "Property", "value": "O3 Gas Sensor (AQICN Hanoi)"},
        "description": {"type": "Property", "value": "Ozone gas concentration sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:AirQuality:Hanoi:AQICN_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 1 hour"}
    },
    
    # ========== WEATHER SENSORS (OpenWeatherMap) ==========
    {
        "id": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Temperature",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["Temperature"]},
        "name": {"type": "Property", "value": "Temperature Sensor (OpenWeatherMap Hanoi)"},
        "description": {"type": "Property", "value": "Ambient air temperature measurement sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8542, 21.0285]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Weather:Hanoi:OpenWeatherMap_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 15 minutes"},
        "measurementAccuracy": {"type": "Property", "value": "±0.5°C"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Humidity",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["Humidity"]},
        "name": {"type": "Property", "value": "Humidity Sensor (OpenWeatherMap Hanoi)"},
        "description": {"type": "Property", "value": "Relative humidity measurement sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8542, 21.0285]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Weather:Hanoi:OpenWeatherMap_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 15 minutes"},
        "measurementAccuracy": {"type": "Property", "value": "±3%"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Pressure",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["Pressure"]},
        "name": {"type": "Property", "value": "Barometric Pressure Sensor (OpenWeatherMap Hanoi)"},
        "description": {"type": "Property", "value": "Atmospheric pressure measurement sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8542, 21.0285]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Weather:Hanoi:OpenWeatherMap_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 15 minutes"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_WindSpeed",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["WindSpeed"]},
        "name": {"type": "Property", "value": "Anemometer (OpenWeatherMap Hanoi)"},
        "description": {"type": "Property", "value": "Wind speed measurement sensor"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8542, 21.0285]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Weather:Hanoi:OpenWeatherMap_Station"},
        "measurementFrequency": {"type": "Property", "value": "every 15 minutes"}
    },
    
    # ========== TRAFFIC SENSORS (TomTom) ==========
    {
        "id": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_HoanKiem",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["VehicleSpeed", "CongestionLevel", "TravelTime"]},
        "name": {"type": "Property", "value": "Traffic Flow Sensor - Hoan Kiem"},
        "description": {"type": "Property", "value": "Traffic monitoring sensor near Hoan Kiem Lake"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8542, 21.0285]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network"},
        "measurementFrequency": {"type": "Property", "value": "every 5 minutes"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_BaDinh",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["VehicleSpeed", "CongestionLevel", "TravelTime"]},
        "name": {"type": "Property", "value": "Traffic Flow Sensor - Ba Dinh"},
        "description": {"type": "Property", "value": "Traffic monitoring sensor in Ba Dinh District"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8342, 21.0368]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network"},
        "measurementFrequency": {"type": "Property", "value": "every 5 minutes"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_MyDinh",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["VehicleSpeed", "CongestionLevel", "TravelTime"]},
        "name": {"type": "Property", "value": "Traffic Flow Sensor - My Dinh"},
        "description": {"type": "Property", "value": "Traffic monitoring sensor in My Dinh area"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.7794, 21.0278]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network"},
        "measurementFrequency": {"type": "Property", "value": "every 5 minutes"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_CauGiay",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["VehicleSpeed", "CongestionLevel", "TravelTime"]},
        "name": {"type": "Property", "value": "Traffic Flow Sensor - Cau Giay"},
        "description": {"type": "Property", "value": "Traffic monitoring sensor in Cau Giay District"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.7947, 21.0333]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network"},
        "measurementFrequency": {"type": "Property", "value": "every 5 minutes"}
    },
    {
        "id": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_LongBien",
        "type": "Sensor",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld", "http://www.w3.org/ns/sosa/", "http://www.w3.org/ns/ssn/"],
        "observes": {"type": "Property", "value": ["VehicleSpeed", "CongestionLevel", "TravelTime"]},
        "name": {"type": "Property", "value": "Traffic Flow Sensor - Long Bien"},
        "description": {"type": "Property", "value": "Traffic monitoring sensor at Long Bien Bridge"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point", "coordinates": [105.8499, 21.0453]}
        },
        "status": {"type": "Property", "value": "active"},
        "isHostedBy": {"type": "Relationship", "object": "urn:ngsi-ld:Platform:Traffic:Hanoi:TomTom_Network"},
        "measurementFrequency": {"type": "Property", "value": "every 5 minutes"}
    }
]


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

async def seed_observable_properties(db: AsyncSession):
    """Seed observable properties to database"""
    repo = EntityRepository(db)
    success_count = 0
    
    print(f"\n🔬 Seeding {len(OBSERVABLE_PROPERTIES)} Observable Properties...")
    
    for prop_data in OBSERVABLE_PROPERTIES:
        try:
            entity = Entity(**prop_data)
            await repo.upsert_entity(entity)
            success_count += 1
            print(f"  ✅ {prop_data['label']['value']}")
        except Exception as e:
            print(f"  ❌ Error: {prop_data['id']} - {str(e)}")
    
    print(f"✅ Seeded {success_count}/{len(OBSERVABLE_PROPERTIES)} Observable Properties\n")
    return success_count


async def seed_features_of_interest(db: AsyncSession):
    """Seed features of interest to database"""
    repo = EntityRepository(db)
    success_count = 0
    
    print(f"\n📍 Seeding {len(FEATURES_OF_INTEREST)} Features of Interest...")
    
    for foi_data in FEATURES_OF_INTEREST:
        try:
            entity = Entity(**foi_data)
            await repo.upsert_entity(entity)
            success_count += 1
            print(f"  ✅ {foi_data['name']['value']}")
        except Exception as e:
            print(f"  ❌ Error: {foi_data['id']} - {str(e)}")
    
    print(f"✅ Seeded {success_count}/{len(FEATURES_OF_INTEREST)} Features of Interest\n")
    return success_count


async def seed_platforms(db: AsyncSession):
    """Seed platforms to database"""
    repo = EntityRepository(db)
    success_count = 0
    
    print(f"\n🏢 Seeding {len(PLATFORMS)} Platforms...")
    
    for platform_data in PLATFORMS:
        try:
            entity = Entity(**platform_data)
            await repo.upsert_entity(entity)
            success_count += 1
            print(f"  ✅ {platform_data['name']['value']}")
        except Exception as e:
            print(f"  ❌ Error: {platform_data['id']} - {str(e)}")
    
    print(f"✅ Seeded {success_count}/{len(PLATFORMS)} Platforms\n")
    return success_count


async def seed_sensors(db: AsyncSession):
    """Seed sensors to database"""
    repo = EntityRepository(db)
    success_count = 0
    
    print(f"\n📡 Seeding {len(SENSORS)} Sensors...")
    
    for sensor_data in SENSORS:
        try:
            entity = Entity(**sensor_data)
            await repo.upsert_entity(entity)
            success_count += 1
            print(f"  ✅ {sensor_data['name']['value']}")
        except Exception as e:
            print(f"  ❌ Error: {sensor_data['id']} - {str(e)}")
    
    print(f"✅ Seeded {success_count}/{len(SENSORS)} Sensors\n")
    return success_count


async def main():
    """Main seeding function"""
    print("=" * 80)
    print("🌱 SOSA/SSN Infrastructure Seeding")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}\n")
    
    async for db in get_db():
        try:
            # Seed in correct order (dependencies)
            total_success = 0
            
            # 1. Observable Properties (no dependencies)
            total_success += await seed_observable_properties(db)
            
            # 2. Features of Interest (no dependencies)
            total_success += await seed_features_of_interest(db)
            
            # 3. Platforms (no dependencies)
            total_success += await seed_platforms(db)
            
            # 4. Sensors (depends on Platforms)
            total_success += await seed_sensors(db)
            
            print("=" * 80)
            print(f"✅ SEEDING COMPLETE")
            print(f"Total entities created: {total_success}")
            print(f"End time: {datetime.now().isoformat()}")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {str(e)}")
            raise
        finally:
            await db.close()
        
        break  # Only run once


if __name__ == "__main__":
    asyncio.run(main())
