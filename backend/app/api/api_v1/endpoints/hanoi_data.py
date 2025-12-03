from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.adapters.osm_overpass import OSMOverpassAdapter
from app.adapters.openweathermap import OpenWeatherMapAdapter
from app.adapters.aqicn import AQICNAdapter
from app.adapters.tomtom import TomTomAdapter
from app.adapters.hanoi_osm_manager import HanoiOSMManager
from app.repositories.entity_repository import EntityRepository
from app.models.ngsi_ld import Entity

router = APIRouter()

# Hanoi coordinates (city center)
HANOI_CENTER = {"lat": 21.0285, "lon": 105.8542}

@router.post("/hanoi/fetch-administrative-boundaries", response_model=Dict[str, Any])
async def fetch_hanoi_boundaries(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Hanoi administrative boundaries from OpenStreetMap.
    This includes districts and wards.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_administrative_boundaries()
        
        saved_count = 0
        errors = []
        
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception as e:
                errors.append({
                    "entity_id": entity_data.get("id"),
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "total_fetched": len(entities_data),
            "saved": saved_count,
            "errors": errors[:10]  # Limit error list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch boundaries: {str(e)}")

@router.post("/hanoi/fetch-hospitals", response_model=Dict[str, Any])
async def fetch_hanoi_hospitals(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all hospitals and clinics in Hanoi from OSM.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_pois(
            poi_type="PointOfInterest",
            amenity_tags=["hospital", "clinic", "doctors"]
        )
        
        saved_count = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception as e:
                continue
        
        return {
            "status": "success",
            "category": "hospitals",
            "total_fetched": len(entities_data),
            "saved": saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-schools", response_model=Dict[str, Any])
async def fetch_hanoi_schools(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all schools and universities in Hanoi from OSM.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_pois(
            poi_type="PointOfInterest",
            amenity_tags=["school", "university", "college", "kindergarten"]
        )
        
        saved_count = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception:
                continue
        
        return {
            "status": "success",
            "category": "schools",
            "total_fetched": len(entities_data),
            "saved": saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-parks", response_model=Dict[str, Any])
async def fetch_hanoi_parks(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all parks and green spaces in Hanoi from OSM.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_pois(
            poi_type="PointOfInterest",
            amenity_tags=["park"]
        )
        
        # Also fetch leisure=park
        query = f"""
        [out:json][timeout:60];
        (
          way["leisure"="park"]({adapter._build_bbox_query()});
          relation["leisure"="park"]({adapter._build_bbox_query()});
        );
        out center;
        """
        
        saved_count = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception:
                continue
        
        return {
            "status": "success",
            "category": "parks",
            "total_fetched": len(entities_data),
            "saved": saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-parking", response_model=Dict[str, Any])
async def fetch_hanoi_parking(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all parking areas in Hanoi from OSM.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_parking_spots()
        
        saved_count = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception:
                continue
        
        return {
            "status": "success",
            "category": "parking",
            "total_fetched": len(entities_data),
            "saved": saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-bus-stops", response_model=Dict[str, Any])
async def fetch_hanoi_bus_stops(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all bus stops in Hanoi from OSM.
    """
    adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.fetch_bus_stops()
        
        saved_count = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                saved_count += 1
            except Exception:
                continue
        
        return {
            "status": "success",
            "category": "bus_stops",
            "total_fetched": len(entities_data),
            "saved": saved_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-weather", response_model=Dict[str, Any])
async def fetch_hanoi_weather(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch current weather data for Hanoi from OpenWeatherMap.
    Creates both WeatherObserved entity and SOSA Observation entities.
    """
    try:
        adapter = OpenWeatherMapAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    try:
        # Fetch returns (WeatherObserved, [Observation entities])
        weather_entity, sosa_observations = await adapter.fetch_weather(
            HANOI_CENTER["lat"],
            HANOI_CENTER["lon"],
            "Hanoi"
        )
        
        # Save legacy entity
        entity = Entity(**weather_entity)
        db_entity = await repo.create_entity(entity)
        
        # Save SOSA observations
        observation_ids = []
        for obs in sosa_observations:
            try:
                obs_entity = Entity(**obs)
                obs_db = await repo.create_entity(obs_entity)
                observation_ids.append(obs_db.id)
            except Exception as e:
                print(f"Warning: Failed to save SOSA observation: {e}")
        
        return {
            "status": "success",
            "entity_id": db_entity.id,
            "type": "WeatherObserved",
            "sosa_observations": len(observation_ids),
            "observation_ids": observation_ids[:5]  # Return first 5
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-air-quality", response_model=Dict[str, Any])
async def fetch_hanoi_air_quality(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch current air quality data for Hanoi from OpenWeatherMap.
    """
    try:
        adapter = OpenWeatherMapAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    try:
        aqi_entity = await adapter.fetch_air_quality(
            HANOI_CENTER["lat"],
            HANOI_CENTER["lon"],
            "Hanoi"
        )
        
        if not aqi_entity:
            raise HTTPException(status_code=404, detail="No air quality data available")
        
        entity = Entity(**aqi_entity)
        db_entity = await repo.create_entity(entity)
        
        return {
            "status": "success",
            "entity_id": db_entity.id,
            "type": "AirQualityObserved",
            "source": "OpenWeatherMap"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hanoi/fetch-air-quality-aqicn", response_model=Dict[str, Any])
async def fetch_hanoi_air_quality_aqicn(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch real-time air quality data from AQICN (WAQI) for Hanoi.
    
    Creates both AirQualityObserved entity and SOSA Observation entities
    for individual pollutants (PM2.5, PM10, O3, NO2, SO2, CO).
    
    AQICN provides fresh, accurate real-time data from government monitoring stations.
    API Documentation: https://aqicn.org/api/
    """
    try:
        adapter = AQICNAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    try:
        # Fetch returns (AirQualityObserved, [Observation entities])
        entity_data, sosa_observations = await adapter.fetch_city_data(city="hanoi")
        
        # Save legacy entity
        entity = Entity(**entity_data)
        db_entity = await repo.create_entity(entity)
        
        # Save SOSA observations
        observation_ids = []
        for obs in sosa_observations:
            try:
                obs_entity = Entity(**obs)
                obs_db = await repo.create_entity(obs_entity)
                observation_ids.append(obs_db.id)
            except Exception as e:
                print(f"Warning: Failed to save SOSA observation: {e}")
        
        return {
            "status": "success",
            "entity_id": db_entity.id,
            "type": "AirQualityObserved",
            "source": "AQICN/WAQI",
            "city": "Hanoi",
            "sosa_observations": len(observation_ids),
            "observation_ids": observation_ids[:7]  # PM2.5, PM10, NO2, SO2, CO, O3, AQI
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AQICN API error: {str(e)}")

@router.post("/vietnam/fetch-air-quality-cities", response_model=Dict[str, Any])
async def fetch_vietnam_cities_air_quality(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch real-time air quality data for major Vietnamese cities from AQICN.
    
    Cities: Hanoi, Ho Chi Minh City (Saigon), Da Nang, Hai Phong, Can Tho
    """
    try:
        adapter = AQICNAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    try:
        # Major Vietnamese cities
        cities = ["hanoi", "saigon", "danang", "haiphong", "cantho"]
        
        entities_data = await adapter.fetch_multiple_cities(cities)
        
        if not entities_data:
            raise HTTPException(
                status_code=404,
                detail="No air quality data available from AQICN"
            )
        
        saved_count = 0
        saved_ids = []
        
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                db_entity = await repo.create_entity(entity)
                saved_count += 1
                saved_ids.append(db_entity.id)
            except Exception:
                # Skip duplicates or invalid entities
                continue
        
        return {
            "status": "success",
            "source": "AQICN/WAQI",
            "total_fetched": len(entities_data),
            "saved": saved_count,
            "entity_ids": saved_ids,
            "cities": cities
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AQICN API error: {str(e)}")

@router.post("/hanoi/fetch-realtime-data", response_model=Dict[str, Any])
async def fetch_hanoi_realtime_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch complete real-time environmental data for Hanoi.
    
    This endpoint fetches and stores:
    1. Weather data (OpenWeatherMap) - temperature, humidity, pressure, wind
    2. Air quality from OpenWeatherMap - PM2.5, PM10, CO, NO2, O3, SO2
    3. Air quality from AQICN - Real-time AQI with detailed pollutants
    
    All data is converted to NGSI-LD format and stored in database.
    """
    repo = EntityRepository(db)
    results = {
        "status": "success",
        "hanoi_data": {},
        "saved_entities": []
    }
    
    # 1. Fetch Weather from OpenWeatherMap
    try:
        weather_adapter = OpenWeatherMapAdapter()
        weather_entity = await weather_adapter.fetch_weather(
            HANOI_CENTER["lat"],
            HANOI_CENTER["lon"],
            "Hanoi"
        )
        
        entity = Entity(**weather_entity)
        db_entity = await repo.create_entity(entity)
        
        results["hanoi_data"]["weather"] = {
            "status": "success",
            "entity_id": db_entity.id,
            "source": "OpenWeatherMap"
        }
        results["saved_entities"].append(db_entity.id)
    except Exception as e:
        results["hanoi_data"]["weather"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 2. Fetch Air Quality from OpenWeatherMap
    try:
        aqi_entity = await weather_adapter.fetch_air_quality(
            HANOI_CENTER["lat"],
            HANOI_CENTER["lon"],
            "Hanoi"
        )
        
        if aqi_entity:
            entity = Entity(**aqi_entity)
            db_entity = await repo.create_entity(entity)
            
            results["hanoi_data"]["air_quality_owm"] = {
                "status": "success",
                "entity_id": db_entity.id,
                "source": "OpenWeatherMap"
            }
            results["saved_entities"].append(db_entity.id)
    except Exception as e:
        results["hanoi_data"]["air_quality_owm"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 3. Fetch Air Quality from AQICN
    try:
        aqicn_adapter = AQICNAdapter()
        aqicn_entity = await aqicn_adapter.fetch_city_data(city="hanoi")
        
        entity = Entity(**aqicn_entity)
        db_entity = await repo.upsert_entity(entity)
        
        results["hanoi_data"]["air_quality_aqicn"] = {
            "status": "success",
            "entity_id": db_entity.id,
            "source": "AQICN/WAQI"
        }
        results["saved_entities"].append(db_entity.id)
    except Exception as e:
        results["hanoi_data"]["air_quality_aqicn"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 4. Fetch Traffic Flow from TomTom
    try:
        tomtom_adapter = TomTomAdapter()
        traffic_entity = await tomtom_adapter.fetch_traffic_flow(
            HANOI_CENTER["lat"],
            HANOI_CENTER["lon"],
            location_name="HanoiCenter"
        )
        
        entity = Entity(**traffic_entity)
        db_entity = await repo.upsert_entity(entity)
        
        results["hanoi_data"]["traffic_flow"] = {
            "status": "success",
            "entity_id": db_entity.id,
            "source": "TomTom Traffic API"
        }
        results["saved_entities"].append(db_entity.id)
    except Exception as e:
        results["hanoi_data"]["traffic_flow"] = {
            "status": "error",
            "error": str(e)
        }
    
    results["total_saved"] = len(results["saved_entities"])
    
    return results

@router.post("/hanoi/fetch-traffic-flow", response_model=Dict[str, Any])
async def fetch_hanoi_traffic_flow(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch real-time traffic flow data for key locations in Hanoi from TomTom.
    
    Monitors traffic at major intersections and roads:
    - Hoan Kiem Lake area (city center)
    - Ba Dinh Square
    - My Dinh area
    - Cau Giay district
    - Long Bien Bridge
    
    Returns TrafficFlowObserved entities with:
    - Current speed vs free-flow speed
    - Congestion level (0-100%)
    - Travel time with traffic
    """
    try:
        adapter = TomTomAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    # Key traffic monitoring points in Hanoi
    traffic_points = [
        {"lat": 21.0285, "lon": 105.8542, "name": "HoanKiem"},
        {"lat": 21.0368, "lon": 105.8342, "name": "BaDinh"},
        {"lat": 21.0278, "lon": 105.7794, "name": "MyDinh"},
        {"lat": 21.0333, "lon": 105.7947, "name": "CauGiay"},
        {"lat": 21.0453, "lon": 105.8499, "name": "LongBien"}
    ]
    
    try:
        entities_data = await adapter.fetch_multiple_traffic_points(traffic_points)
        
        if not entities_data:
            raise HTTPException(
                status_code=404,
                detail="No traffic flow data available"
            )
        
        saved_count = 0
        saved_ids = []
        
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                db_entity = await repo.upsert_entity(entity)
                saved_count += 1
                saved_ids.append(db_entity.id)
            except Exception:
                continue
        
        return {
            "status": "success",
            "source": "TomTom Traffic API",
            "total_fetched": len(entities_data),
            "saved": saved_count,
            "entity_ids": saved_ids,
            "monitoring_points": [p["name"] for p in traffic_points]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TomTom API error: {str(e)}")

@router.post("/hanoi/fetch-traffic-incidents", response_model=Dict[str, Any])
async def fetch_hanoi_traffic_incidents(
    severity: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch real-time traffic incidents in Hanoi from TomTom Traffic Incidents API.
    
    Incident types include:
    - 🚗 Accidents (tai nạn giao thông)
    - 🚧 Road closures (đường bị đóng)
    - 👷 Road works/construction (thi công)
    - ⚠️ Dangerous conditions (điều kiện nguy hiểm)
    - 🌧️ Weather-related (mưa, sương mù, băng giá)
    - 🚦 Traffic jams (tắc đường)
    - 🚙 Broken down vehicles (xe hỏng)
    
    Args:
        severity: Filter by severity level
            - 1: Minor (nhẹ)
            - 2: Moderate (vừa phải)
            - 3: Major (nghiêm trọng)
            - None: All severities
    
    Returns:
        TrafficEvent entities with:
        - Incident type and severity
        - Location (coordinates)
        - Description in English
        - Affected road segments
        - Expected delay (seconds)
        - Start/end time
    """
    try:
        adapter = TomTomAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    # Hanoi bounding box
    hanoi_bbox = {
        "min_lat": 20.53,
        "max_lat": 21.38,
        "min_lon": 105.29,
        "max_lon": 106.02
    }
    
    try:
        entities_data = await adapter.fetch_traffic_incidents(
            bbox=hanoi_bbox,
            severity=str(severity) if severity else None
        )
        
        if not entities_data:
            return {
                "status": "success",
                "message": "No active traffic incidents in Hanoi",
                "total_fetched": 0,
                "saved": 0,
                "entity_ids": []
            }
        
        saved_count = 0
        saved_ids = []
        incident_summary = {}
        
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                db_entity = await repo.upsert_entity(entity)
                saved_count += 1
                saved_ids.append(db_entity.id)
                
                # Count by type
                incident_type = entity_data.get("eventType", {}).get("value", "unknown")
                incident_summary[incident_type] = incident_summary.get(incident_type, 0) + 1
            except Exception as e:
                print(f"Error saving incident: {e}")
                continue
        
        return {
            "status": "success",
            "source": "TomTom Traffic Incidents API",
            "total_fetched": len(entities_data),
            "saved": saved_count,
            "entity_ids": saved_ids,
            "incident_summary": incident_summary,
            "bbox": hanoi_bbox,
            "severity_filter": severity if severity else "all"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TomTom API error: {str(e)}")

@router.post("/hanoi/fetch-pois-tomtom", response_model=Dict[str, Any])
async def fetch_hanoi_pois_tomtom(
    category: str = "hospital",
    radius: int = 5000,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for Points of Interest in Hanoi using TomTom Places API.
    
    Args:
        category: POI category (hospital, restaurant, school, parking, etc.)
        radius: Search radius in meters from city center (default 5km)
    
    TomTom provides commercial POI data with:
    - Accurate names and addresses
    - Phone numbers
    - Category classifications
    - Distance from center
    """
    try:
        adapter = TomTomAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    
    try:
        entities_data = await adapter.search_pois(
            category=category,
            lat=HANOI_CENTER["lat"],
            lon=HANOI_CENTER["lon"],
            radius=radius,
            limit=20
        )
        
        if not entities_data:
            raise HTTPException(
                status_code=404,
                detail=f"No {category} POIs found in Hanoi"
            )
        
        saved_count = 0
        saved_ids = []
        
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                db_entity = await repo.upsert_entity(entity)
                saved_count += 1
                saved_ids.append(db_entity.id)
            except Exception:
                continue
        
        return {
            "status": "success",
            "source": "TomTom Places API",
            "category": category,
            "total_fetched": len(entities_data),
            "saved": saved_count,
            "entity_ids": saved_ids[:5],
            "search_params": {
                "center": HANOI_CENTER,
                "radius_meters": radius
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TomTom API error: {str(e)}")

@router.post("/hanoi/fetch-all-data", response_model=Dict[str, Any])
async def fetch_all_hanoi_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all available data for Hanoi.
    This is a comprehensive data ingestion endpoint.
    """
    results = {}
    
    # Fetch OSM data
    osm_adapter = OSMOverpassAdapter()
    repo = EntityRepository(db)
    
    try:
        # Administrative boundaries
        boundaries = await osm_adapter.fetch_administrative_boundaries()
        results["boundaries"] = {"fetched": len(boundaries), "saved": 0}
        for entity_data in boundaries:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                results["boundaries"]["saved"] += 1
            except:
                pass
        
        # Hospitals
        hospitals = await osm_adapter.fetch_pois("PointOfInterest", ["hospital", "clinic"])
        results["hospitals"] = {"fetched": len(hospitals), "saved": 0}
        for entity_data in hospitals:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                results["hospitals"]["saved"] += 1
            except:
                pass
        
        # Schools
        schools = await osm_adapter.fetch_pois("PointOfInterest", ["school", "university"])
        results["schools"] = {"fetched": len(schools), "saved": 0}
        for entity_data in schools:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                results["schools"]["saved"] += 1
            except:
                pass
        
        # Parking
        parking = await osm_adapter.fetch_parking_spots()
        results["parking"] = {"fetched": len(parking), "saved": 0}
        for entity_data in parking:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                results["parking"]["saved"] += 1
            except:
                pass
        
        # Bus stops
        bus_stops = await osm_adapter.fetch_bus_stops()
        results["bus_stops"] = {"fetched": len(bus_stops), "saved": 0}
        for entity_data in bus_stops:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                results["bus_stops"]["saved"] += 1
            except:
                pass
        
        # Weather (if API key available)
        try:
            weather_adapter = OpenWeatherMapAdapter()
            weather_entity = await weather_adapter.fetch_weather(
                HANOI_CENTER["lat"],
                HANOI_CENTER["lon"],
                "Hanoi"
            )
            entity = Entity(**weather_entity)
            await repo.create_entity(entity)
            results["weather"] = {"status": "success"}
        except:
            results["weather"] = {"status": "skipped"}
        
        return {
            "status": "completed",
            "city": "Hanoi",
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vietnam/fetch-realtime-data", response_model=Dict[str, Any])
async def fetch_realtime_vietnam_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch real-time environmental data for Vietnam cities.
    
    Sources:
    - OpenWeatherMap: Weather data for major cities
    - OpenWeatherMap: Air quality (AQI) for major cities
    - OpenAQ: Government air quality monitoring stations
    
    Returns comprehensive real-time environmental data.
    """
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sources": []
    }
    repo = EntityRepository(db)
    
    # Major Vietnam cities
    cities = [
        {"name": "Hanoi", "lat": 21.0285, "lon": 105.8542},
        {"name": "Ho Chi Minh City", "lat": 10.8231, "lon": 106.6297},
        {"name": "Da Nang", "lat": 16.0544, "lon": 108.2022},
        {"name": "Hai Phong", "lat": 20.8449, "lon": 106.6881},
        {"name": "Can Tho", "lat": 10.0452, "lon": 105.7469}
    ]
    
    # 1. Fetch Weather from OpenWeatherMap
    weather_results = {"saved": 0, "errors": 0}
    try:
        weather_adapter = OpenWeatherMapAdapter()
        for city in cities:
            try:
                weather_entity = await weather_adapter.fetch_weather(
                    city["lat"], city["lon"], city["name"]
                )
                entity = Entity(**weather_entity)
                await repo.create_entity(entity)
                weather_results["saved"] += 1
            except Exception:
                weather_results["errors"] += 1
        
        results["sources"].append({
            "name": "OpenWeatherMap - Weather",
            "status": "success",
            "saved": weather_results["saved"],
            "errors": weather_results["errors"]
        })
    except Exception as e:
        results["sources"].append({
            "name": "OpenWeatherMap - Weather",
            "status": "failed",
            "error": str(e)
        })
    
    # 2. Fetch AQI from OpenWeatherMap
    aqi_owm_results = {"saved": 0, "errors": 0}
    try:
        for city in cities:
            try:
                aqi_entity = await weather_adapter.fetch_air_quality(
                    city["lat"], city["lon"], city["name"]
                )
                if aqi_entity:
                    entity = Entity(**aqi_entity)
                    await repo.create_entity(entity)
                    aqi_owm_results["saved"] += 1
            except Exception:
                aqi_owm_results["errors"] += 1
        
        results["sources"].append({
            "name": "OpenWeatherMap - Air Quality",
            "status": "success",
            "saved": aqi_owm_results["saved"],
            "errors": aqi_owm_results["errors"]
        })
    except Exception as e:
        results["sources"].append({
            "name": "OpenWeatherMap - Air Quality",
            "status": "failed",
            "error": str(e)
        })
    
    # 3. Fetch from OpenAQ (Government stations)
    try:
        openaq_adapter = OpenAQAdapter()
        entities_data = await openaq_adapter.fetch_latest_measurements(
            country="VN",
            limit=100
        )
        
        openaq_saved = 0
        for entity_data in entities_data:
            try:
                entity = Entity(**entity_data)
                await repo.create_entity(entity)
                openaq_saved += 1
            except Exception:
                continue
        
        results["sources"].append({
            "name": "OpenAQ - Government Stations",
            "status": "success",
            "fetched": len(entities_data),
            "saved": openaq_saved
        })
    except Exception as e:
        results["sources"].append({
            "name": "OpenAQ - Government Stations",
            "status": "failed",
            "error": str(e)
        })
    
    return results


# ============================================================================
# COMPLETE HANOI ADMINISTRATIVE STRUCTURE ENDPOINTS
# ============================================================================

@router.post("/hanoi/fetch-city-boundary", response_model=Dict[str, Any])
async def fetch_city_boundary(
    db: AsyncSession = Depends(get_db)
):
    """
    Test endpoint: Fetch only Hanoi city boundary.
    """
    manager = HanoiOSMManager()
    repo = EntityRepository(db)
    
    try:
        city_entity = await manager.fetch_hanoi_boundary()
        # Directly save dict to repository (it handles validation)
        await repo.upsert_entity(city_entity)
        
        return {
            "status": "success",
            "city": city_entity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hanoi/fetch-districts-only", response_model=Dict[str, Any])
async def fetch_districts_only(
    db: AsyncSession = Depends(get_db)
):
    """
    Test endpoint: Fetch only districts without wards.
    """
    manager = HanoiOSMManager()
    repo = EntityRepository(db)
    
    try:
        districts = await manager.fetch_districts()
        
        saved = 0
        for district_data in districts:
            try:
                await repo.upsert_entity(district_data)
                saved += 1
            except Exception as e:
                print(f"Error saving district: {e}")
        
        return {
            "status": "success",
            "total": len(districts),
            "saved": saved,
            "districts": districts[:5]  # Sample
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hanoi/fetch-complete-admin-structure", response_model=Dict[str, Any])
async def fetch_complete_admin_structure(
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch complete Hanoi administrative structure:
    - City boundary (admin_level 4)
    - All districts (admin_level 6) - Quận/Huyện
    - All wards (admin_level 8) - Phường/Xã
    
    Creates hierarchical relationships between levels.
    """
    manager = HanoiOSMManager()
    repo = EntityRepository(db)
    
    results = {
        "status": "in_progress",
        "timestamp": datetime.utcnow().isoformat(),
        "city": None,
        "districts": {"total": 0, "saved": 0, "errors": []},
        "wards": {"total": 0, "saved": 0, "errors": []}
    }
    
    try:
        # 1. Fetch Hanoi city boundary
        print("Fetching Hanoi city boundary...")
        city_entity = await manager.fetch_hanoi_boundary()
        try:
            await repo.upsert_entity(city_entity)
            results["city"] = {
                "name": city_entity["name"]["value"],
                "id": city_entity["id"],
                "saved": True
            }
        except Exception as e:
            results["city"] = {
                "error": str(e),
                "saved": False
            }
        
        # 2. Fetch all districts
        print("Fetching districts...")
        districts = await manager.fetch_districts()
        results["districts"]["total"] = len(districts)
        
        for district_data in districts:
            try:
                await repo.upsert_entity(district_data)
                results["districts"]["saved"] += 1
            except Exception as e:
                results["districts"]["errors"].append({
                    "id": district_data.get("id"),
                    "name": district_data.get("name", {}).get("value"),
                    "error": str(e)
                })
        
        # 3. Fetch all wards
        print("Fetching wards...")
        wards = await manager.fetch_all_wards()
        results["wards"]["total"] = len(wards)
        
        for ward_data in wards:
            try:
                await repo.upsert_entity(ward_data)
                results["wards"]["saved"] += 1
            except Exception as e:
                results["wards"]["errors"].append({
                    "id": ward_data.get("id"),
                    "name": ward_data.get("name", {}).get("value"),
                    "error": str(e)
                })
        
        results["status"] = "success"
        return results
        
    except Exception as e:
        results["status"] = "failed"
        results["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hanoi/fetch-all-facilities", response_model=Dict[str, Any])
async def fetch_all_facilities(
    categories: List[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all facilities in Hanoi, organized by category:
    - healthcare: hospitals, clinics, pharmacies
    - education: schools, universities, libraries
    - parks: parks, playgrounds
    - sports: sports centers, stadiums
    - culture: museums, theatres, cinemas
    - public_services: police, fire stations, post offices
    - transportation: bus stations, taxi stands
    - emergency: combined emergency services
    - worship: religious places
    - food: restaurants, cafes
    - shopping: markets, supermarkets
    
    Args:
        categories: Optional list to filter specific categories
    """
    manager = HanoiOSMManager()
    repo = EntityRepository(db)
    
    results = {
        "status": "in_progress",
        "timestamp": datetime.utcnow().isoformat(),
        "categories": {}
    }
    
    try:
        # Fetch facilities by category
        facilities_by_category = await manager.fetch_facilities_in_area(
            categories=categories
        )
        
        # Save all facilities to database
        for category, facilities in facilities_by_category.items():
            saved_count = 0
            errors = []
            
            for facility_data in facilities:
                try:
                    await repo.upsert_entity(facility_data)
                    saved_count += 1
                except Exception as e:
                    errors.append({
                        "id": facility_data.get("id"),
                        "name": facility_data.get("name", {}).get("value"),
                        "error": str(e)
                    })
            
            results["categories"][category] = {
                "total": len(facilities),
                "saved": saved_count,
                "errors_count": len(errors),
                "errors": errors[:5]  # Only show first 5 errors
            }
        
        results["status"] = "success"
        results["summary"] = {
            "total_categories": len(facilities_by_category),
            "total_facilities": sum(len(f) for f in facilities_by_category.values()),
            "total_saved": sum(r["saved"] for r in results["categories"].values())
        }
        
        return results
        
    except Exception as e:
        results["status"] = "failed"
        results["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hanoi/admin-hierarchy", response_model=Dict[str, Any])
async def get_admin_hierarchy(
    db: AsyncSession = Depends(get_db)
):
    """
    Get hierarchical view of Hanoi administrative structure.
    Returns nested structure: City → Districts → Wards
    """
    repo = EntityRepository(db)
    
    try:
        # Query all administrative areas
        city = await repo.get_entities_by_type("AdministrativeArea", limit=1, filters={
            "administrativeLevel.value": "City"
        })
        
        districts = await repo.get_entities_by_type("AdministrativeArea", limit=100, filters={
            "administrativeLevel.value": "District"
        })
        
        wards = await repo.get_entities_by_type("AdministrativeArea", limit=1000, filters={
            "administrativeLevel.value": "Ward"
        })
        
        hierarchy = {
            "city": city[0] if city else None,
            "statistics": {
                "total_districts": len(districts),
                "total_wards": len(wards)
            },
            "districts": [
                {
                    "id": d["id"],
                    "name": d.get("name", {}).get("value"),
                    "alternateName": d.get("alternateName", {}).get("value"),
                    "adminLevel": d.get("adminLevel", {}).get("value"),
                    "wards_count": len([w for w in wards if w.get("refDistrict", {}).get("object") == d["id"]])
                }
                for d in districts
            ]
        }
        
        return hierarchy
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hanoi/facilities-by-ward/{ward_id}", response_model=Dict[str, Any])
async def get_facilities_by_ward(
    ward_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all facilities within a specific ward.
    Uses spatial query to find POIs within ward boundaries.
    """
    repo = EntityRepository(db)
    
    try:
        # Get ward boundary
        ward = await repo.get_entity_by_id(ward_id)
        if not ward:
            raise HTTPException(status_code=404, detail="Ward not found")
        
        # Query facilities (this is simplified - would need PostGIS spatial query)
        facilities = await repo.get_entities_by_type("PointOfInterest", limit=1000)
        
        # TODO: Add spatial filtering using PostGIS ST_Within
        # For now, return all facilities with ward info
        
        return {
            "ward": {
                "id": ward["id"],
                "name": ward.get("name", {}).get("value"),
                "alternateName": ward.get("alternateName", {}).get("value")
            },
            "facilities_count": len(facilities),
            "facilities": facilities[:50]  # Limit to 50 for response size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

