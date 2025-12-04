# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.adapters.openweathermap import OpenWeatherMapAdapter
from app.repositories.entity_repository import EntityRepository
from app.models.ngsi_ld import Entity

router = APIRouter()

# Vietnam cities coordinates
VIETNAM_CITIES = {
    "Hanoi": {"lat": 21.0285, "lon": 105.8542},
    "HoChiMinh": {"lat": 10.8231, "lon": 106.6297},
    "DaNang": {"lat": 16.0544, "lon": 108.2022},
    "HaiPhong": {"lat": 20.8449, "lon": 106.6881},
    "CanTho": {"lat": 10.0452, "lon": 105.7469}
}

@router.post("/fetch-weather", response_model=List[dict])
async def fetch_weather_data(
    cities: List[str] = Query(default=["Hanoi", "HoChiMinh"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch weather data from OpenWeatherMap for specified Vietnamese cities
    and store as NGSI-LD entities.
    """
    try:
        adapter = OpenWeatherMapAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    results = []
    
    for city in cities:
        if city not in VIETNAM_CITIES:
            continue
        
        coords = VIETNAM_CITIES[city]
        
        try:
            # Fetch weather data
            weather_entity = await adapter.fetch_weather(
                coords["lat"], 
                coords["lon"], 
                city
            )
            
            # Convert to Entity model
            entity = Entity(**weather_entity)
            
            # Save to database
            db_entity = await repo.create_entity(entity)
            results.append({
                "city": city,
                "type": "WeatherObserved",
                "entity_id": db_entity.id,
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "city": city,
                "type": "WeatherObserved",
                "error": str(e),
                "status": "failed"
            })
    
    return results

@router.post("/fetch-air-quality", response_model=List[dict])
async def fetch_air_quality_data(
    cities: List[str] = Query(default=["Hanoi", "HoChiMinh"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch air quality data from OpenWeatherMap for specified Vietnamese cities
    and store as NGSI-LD entities.
    """
    try:
        adapter = OpenWeatherMapAdapter()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    repo = EntityRepository(db)
    results = []
    
    for city in cities:
        if city not in VIETNAM_CITIES:
            continue
        
        coords = VIETNAM_CITIES[city]
        
        try:
            # Fetch air quality data
            aqi_entity = await adapter.fetch_air_quality(
                coords["lat"], 
                coords["lon"], 
                city
            )
            
            if not aqi_entity:
                results.append({
                    "city": city,
                    "type": "AirQualityObserved",
                    "status": "no_data"
                })
                continue
            
            # Convert to Entity model
            entity = Entity(**aqi_entity)
            
            # Save to database
            db_entity = await repo.create_entity(entity)
            results.append({
                "city": city,
                "type": "AirQualityObserved",
                "entity_id": db_entity.id,
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "city": city,
                "type": "AirQualityObserved",
                "error": str(e),
                "status": "failed"
            })
    
    return results

