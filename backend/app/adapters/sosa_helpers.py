# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
SOSA/SSN Helper Functions

Utilities for creating SOSA-compliant Observation entities from adapter data.
These functions convert legacy entity formats (WeatherObserved, AirQualityObserved)
to proper SOSA Observation entities with madeBySensor relationships.

Author: CityLens Development Team
License: GPL-3.0
Date: 2025-12-03
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


# Mapping of observable property names to URNs
OBSERVABLE_PROPERTY_URNS = {
    # Air Quality
    "PM2.5": "urn:ngsi-ld:ObservableProperty:AirQuality:PM2.5",
    "PM10": "urn:ngsi-ld:ObservableProperty:AirQuality:PM10",
    "NO2": "urn:ngsi-ld:ObservableProperty:AirQuality:NO2",
    "SO2": "urn:ngsi-ld:ObservableProperty:AirQuality:SO2",
    "CO": "urn:ngsi-ld:ObservableProperty:AirQuality:CO",
    "O3": "urn:ngsi-ld:ObservableProperty:AirQuality:O3",
    "AQI": "urn:ngsi-ld:ObservableProperty:AirQuality:AQI",
    
    # Weather
    "Temperature": "urn:ngsi-ld:ObservableProperty:Weather:Temperature",
    "Humidity": "urn:ngsi-ld:ObservableProperty:Weather:Humidity",
    "Pressure": "urn:ngsi-ld:ObservableProperty:Weather:Pressure",
    "WindSpeed": "urn:ngsi-ld:ObservableProperty:Weather:WindSpeed",
    
    # Traffic
    "VehicleSpeed": "urn:ngsi-ld:ObservableProperty:Traffic:VehicleSpeed",
    "CongestionLevel": "urn:ngsi-ld:ObservableProperty:Traffic:CongestionLevel",
    "TravelTime": "urn:ngsi-ld:ObservableProperty:Traffic:TravelTime"
}


# Mapping of sensor IDs
SENSOR_URNS = {
    # AQICN Air Quality Sensors
    "aqicn_pm25": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM25",
    "aqicn_pm10": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_PM10",
    "aqicn_no2": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_NO2",
    "aqicn_so2": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_SO2",
    "aqicn_co": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_CO",
    "aqicn_o3": "urn:ngsi-ld:Sensor:AirQuality:Hanoi:AQICN_O3",
    
    # OpenWeatherMap Weather Sensors
    "owm_temperature": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Temperature",
    "owm_humidity": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Humidity",
    "owm_pressure": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_Pressure",
    "owm_windspeed": "urn:ngsi-ld:Sensor:Weather:Hanoi:OWM_WindSpeed",
    
    # TomTom Traffic Sensors
    "tomtom_hoankiem": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_HoanKiem",
    "tomtom_badinh": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_BaDinh",
    "tomtom_mydinh": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_MyDinh",
    "tomtom_caugiay": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_CauGiay",
    "tomtom_longbien": "urn:ngsi-ld:Sensor:Traffic:Hanoi:TomTom_LongBien"
}


# Features of Interest URNs
FEATURE_URNS = {
    "hanoi_city": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:City",
    "hanoi_hoankiem": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:HoanKiem",
    "hanoi_badinh": "urn:ngsi-ld:FeatureOfInterest:Location:Hanoi:BaDinh",
    "hanoi_air": "urn:ngsi-ld:FeatureOfInterest:AirVolume:Hanoi:Urban",
    "hanoi_road_hoankiem": "urn:ngsi-ld:FeatureOfInterest:RoadSegment:Hanoi:HoanKiem"
}


def create_sosa_observation(
    observable_property: str,
    sensor_key: str,
    feature_key: str,
    result_value: Any,
    result_time: Optional[str] = None,
    unit_code: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None,
    quality_flag: str = "good"
) -> Dict[str, Any]:
    """
    Create a SOSA-compliant Observation entity.
    
    Args:
        observable_property: Property name (e.g., "PM2.5", "Temperature")
        sensor_key: Sensor key from SENSOR_URNS mapping
        feature_key: Feature key from FEATURE_URNS mapping
        result_value: Measured value
        result_time: ISO 8601 timestamp (default: now)
        unit_code: UN/CEFACT unit code
        location: GeoJSON location (optional)
        quality_flag: Data quality (good, suspect, bad)
    
    Returns:
        SOSA Observation entity dict
    """
    if result_time is None:
        result_time = datetime.utcnow().isoformat() + "Z"
    
    # Get URNs
    observable_property_urn = OBSERVABLE_PROPERTY_URNS.get(observable_property)
    sensor_urn = SENSOR_URNS.get(sensor_key)
    feature_urn = FEATURE_URNS.get(feature_key)
    
    if not observable_property_urn:
        raise ValueError(f"Unknown observable property: {observable_property}")
    if not sensor_urn:
        raise ValueError(f"Unknown sensor key: {sensor_key}")
    if not feature_urn:
        raise ValueError(f"Unknown feature key: {feature_key}")
    
    # Generate observation ID
    timestamp = int(datetime.fromisoformat(result_time.replace("Z", "+00:00")).timestamp())
    obs_id = f"urn:ngsi-ld:Observation:{observable_property.replace('.', '')}:{sensor_key}:{timestamp}"
    
    entity = {
        "id": obs_id,
        "type": "Observation",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "http://www.w3.org/ns/sosa/"
        ],
        "madeBySensor": {
            "type": "Relationship",
            "object": sensor_urn
        },
        "observedProperty": {
            "type": "Relationship",
            "object": observable_property_urn
        },
        "hasFeatureOfInterest": {
            "type": "Relationship",
            "object": feature_urn
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
        },
        "qualityFlag": {
            "type": "Property",
            "value": quality_flag
        }
    }
    
    if unit_code:
        entity["hasResult"]["unitCode"] = unit_code
    
    if location:
        entity["location"] = {
            "type": "GeoProperty",
            "value": location
        }
    
    return entity


def create_multiple_sosa_observations(
    observations: List[Dict[str, Any]],
    sensor_key: str,
    feature_key: str,
    result_time: Optional[str] = None,
    location: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Create multiple SOSA Observation entities from a list.
    
    Useful when a single data source provides multiple measurements
    (e.g., AQICN returns PM2.5, PM10, NO2, etc. at once).
    
    Args:
        observations: List of dicts with keys: observable_property, value, unit_code
        sensor_key: Base sensor key (will be adjusted per observable property)
        feature_key: Feature of interest key
        result_time: ISO 8601 timestamp (default: now)
        location: GeoJSON location (optional)
    
    Returns:
        List of SOSA Observation entities
    
    Example:
        observations = [
            {"observable_property": "PM2.5", "value": 25.5, "unit_code": "GQ"},
            {"observable_property": "PM10", "value": 45.0, "unit_code": "GQ"},
            {"observable_property": "NO2", "value": 15.0, "unit_code": "GQ"}
        ]
    """
    entities = []
    
    for obs in observations:
        try:
            # Adjust sensor key based on observable property
            prop = obs["observable_property"]
            adjusted_sensor_key = f"{sensor_key}_{prop.lower().replace('.', '')}"
            
            entity = create_sosa_observation(
                observable_property=prop,
                sensor_key=adjusted_sensor_key,
                feature_key=feature_key,
                result_value=obs["value"],
                result_time=result_time,
                unit_code=obs.get("unit_code"),
                location=location,
                quality_flag=obs.get("quality_flag", "good")
            )
            entities.append(entity)
        except Exception as e:
            print(f"Warning: Failed to create observation for {obs.get('observable_property')}: {e}")
            continue
    
    return entities


def augment_legacy_entity_with_sosa(
    legacy_entity: Dict[str, Any],
    sensor_key: str,
    feature_key: str
) -> Dict[str, Any]:
    """
    Add SOSA relationships to legacy entities (WeatherObserved, AirQualityObserved).
    
    This allows backward compatibility - keeping the original entity structure
    while adding SOSA metadata.
    
    Args:
        legacy_entity: Existing entity (WeatherObserved, AirQualityObserved, etc.)
        sensor_key: Sensor key for primary sensor
        feature_key: Feature of interest key
    
    Returns:
        Enhanced entity with SOSA relationships
    """
    sensor_urn = SENSOR_URNS.get(sensor_key)
    feature_urn = FEATURE_URNS.get(feature_key)
    
    if sensor_urn:
        legacy_entity["madeBySensor"] = {
            "type": "Relationship",
            "object": sensor_urn
        }
    
    if feature_urn:
        legacy_entity["hasFeatureOfInterest"] = {
            "type": "Relationship",
            "object": feature_urn
        }
    
    # Add SOSA context if not present
    if "@context" in legacy_entity:
        contexts = legacy_entity["@context"]
        if isinstance(contexts, list):
            if "http://www.w3.org/ns/sosa/" not in contexts:
                legacy_entity["@context"].append("http://www.w3.org/ns/sosa/")
        elif "http://www.w3.org/ns/sosa/" not in contexts:
            legacy_entity["@context"] = [contexts, "http://www.w3.org/ns/sosa/"]
    
    return legacy_entity


# Convenience functions for common scenarios

def create_aqi_observations_from_aqicn(
    aqi_data: Dict[str, Any],
    city: str = "hanoi"
) -> List[Dict[str, Any]]:
    """
    Create SOSA observations from AQICN API response.
    
    AQICN Response Structure:
    {
        "aqi": 71,
        "idx": 7397,
        "time": {"s": "2016-12-10 19:00:00", "tz": "-06:00", "v": 1481396400},
        "city": {"name": "Chicago, Illinois", "geo": [41.9136, -87.7239]},
        "iaqi": {
            "pm25": {"v": 71},
            "pm10": {"v": 45},
            "o3": {"v": 30},
            "no2": {"v": 15},
            "so2": {"v": 5},
            "co": {"v": 0.3}
        },
        "forecast": {
            "daily": {
                "pm25": [{"avg": 154, "day": "2020-06-13", "max": 157, "min": 131}]
            }
        }
    }
    
    Args:
        aqi_data: Raw AQICN API response data
        city: City name (default: hanoi)
    
    Returns:
        List of SOSA Observation entities for all available pollutants
    """
    # Extract timestamp
    time_info = aqi_data.get("time", {})
    time_str = time_info.get("s", "")
    tz = time_info.get("tz", "+00:00")
    
    if time_str:
        try:
            # Convert "2016-12-10 19:00:00" to ISO 8601
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            result_time = dt.isoformat() + tz
        except:
            result_time = datetime.utcnow().isoformat() + "Z"
    else:
        result_time = datetime.utcnow().isoformat() + "Z"
    
    # Extract location
    location = None
    if "city" in aqi_data and "geo" in aqi_data["city"]:
        geo = aqi_data["city"]["geo"]
        if len(geo) >= 2:
            location = {
                "type": "Point",
                "coordinates": [float(geo[1]), float(geo[0])]  # lon, lat
            }
    
    # Extract individual pollutants from iaqi
    iaqi = aqi_data.get("iaqi", {})
    
    # Mapping: (Property Name, iaqi key, unit code)
    pollutants = [
        ("PM2.5", "pm25", "GQ"),  # µg/m³
        ("PM10", "pm10", "GQ"),   # µg/m³
        ("NO2", "no2", "GQ"),     # µg/m³
        ("SO2", "so2", "GQ"),     # µg/m³
        ("CO", "co", "GP"),       # mg/m³
        ("O3", "o3", "GQ")        # µg/m³
    ]
    
    obs_list = []
    for prop_name, iaqi_key, unit in pollutants:
        if iaqi_key in iaqi:
            value_data = iaqi[iaqi_key]
            if isinstance(value_data, dict) and "v" in value_data:
                value = value_data["v"]
                # Handle numeric values
                if isinstance(value, (int, float)) and value >= 0:
                    obs_list.append({
                        "observable_property": prop_name,
                        "value": float(value),
                        "unit_code": unit
                    })
    
    # Note: Overall AQI is derived from individual pollutants, not a separate sensor measurement
    # So we don't create a separate SOSA Observation for it
    
    if not obs_list:
        print(f"Warning: No pollutant data found in AQICN response for {city}")
    
    return create_multiple_sosa_observations(
        observations=obs_list,
        sensor_key="aqicn",
        feature_key="hanoi_air",
        result_time=result_time,
        location=location
    )


def create_weather_observations_from_owm(
    weather_data: Dict[str, Any],
    city: str = "hanoi"
) -> List[Dict[str, Any]]:
    """
    Create SOSA observations from OpenWeatherMap API response.
    
    Args:
        weather_data: Raw OWM API response
        city: City name (default: hanoi)
    
    Returns:
        List of SOSA Observation entities
    """
    result_time = datetime.utcnow().isoformat() + "Z"
    
    location = None
    if "coord" in weather_data:
        location = {
            "type": "Point",
            "coordinates": [weather_data["coord"]["lon"], weather_data["coord"]["lat"]]
        }
    
    obs_list = []
    
    if "main" in weather_data:
        main = weather_data["main"]
        
        if "temp" in main:
            obs_list.append({
                "observable_property": "Temperature",
                "value": main["temp"],
                "unit_code": "CEL"
            })
        
        if "humidity" in main:
            obs_list.append({
                "observable_property": "Humidity",
                "value": main["humidity"],
                "unit_code": "P1"
            })
        
        if "pressure" in main:
            obs_list.append({
                "observable_property": "Pressure",
                "value": main["pressure"],
                "unit_code": "A97"
            })
    
    if "wind" in weather_data and "speed" in weather_data["wind"]:
        obs_list.append({
            "observable_property": "WindSpeed",
            "value": weather_data["wind"]["speed"],
            "unit_code": "MTS"
        })
    
    return create_multiple_sosa_observations(
        observations=obs_list,
        sensor_key="owm",
        feature_key="hanoi_city",
        result_time=result_time,
        location=location
    )


def create_traffic_observations_from_tomtom(
    traffic_data: Dict[str, Any],
    location_name: str = "HoanKiem"
) -> List[Dict[str, Any]]:
    """
    Create SOSA observations from TomTom Traffic API response.
    
    Args:
        traffic_data: Raw TomTom API response
        location_name: Location name (HoanKiem, BaDinh, etc.)
    
    Returns:
        List of SOSA Observation entities
    """
    result_time = datetime.utcnow().isoformat() + "Z"
    sensor_key = f"tomtom_{location_name.lower()}"
    feature_key = "hanoi_road_hoankiem"  # Default, can be dynamic
    
    obs_list = []
    
    if "currentSpeed" in traffic_data:
        obs_list.append({
            "observable_property": "VehicleSpeed",
            "value": traffic_data["currentSpeed"],
            "unit_code": "KMH"
        })
    
    if "freeFlowSpeed" in traffic_data and "currentSpeed" in traffic_data:
        congestion = 1 - (traffic_data["currentSpeed"] / traffic_data["freeFlowSpeed"])
        obs_list.append({
            "observable_property": "CongestionLevel",
            "value": round(congestion, 2),
            "unit_code": "C62"
        })
    
    if "currentTravelTime" in traffic_data:
        obs_list.append({
            "observable_property": "TravelTime",
            "value": traffic_data["currentTravelTime"],
            "unit_code": "SEC"
        })
    
    location = None
    if "coordinates" in traffic_data:
        coords = traffic_data["coordinates"]
        location = {
            "type": "Point",
            "coordinates": [coords["lon"], coords["lat"]]
        }
    
    return create_multiple_sosa_observations(
        observations=obs_list,
        sensor_key=sensor_key,
        feature_key=feature_key,
        result_time=result_time,
        location=location
    )
