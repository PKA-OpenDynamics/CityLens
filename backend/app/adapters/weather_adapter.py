# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

import httpx
import logging
from datetime import datetime
from typing import List
from app.models.ngsi_ld import Entity, Property, GeoProperty

logger = logging.getLogger(__name__)

class WeatherAdapter:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def fetch_weather(self, city: str, lat: float = None, lon: float = None) -> dict:
        """Fetch raw weather data from OpenWeatherMap"""
        params = {"appid": self.api_key, "units": "metric"}
        if lat is not None and lon is not None:
            params.update({"lat": lat, "lon": lon})
        else:
            params.update({"q": city})

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()

    def to_ngsi_ld(self, raw_data: dict) -> Entity:
        """Convert OWM JSON to NGSI-LD WeatherObserved Entity"""
        
        # Unique ID generation: urn:ngsi-ld:WeatherObserved:{CityName}
        city_name = raw_data.get("name", "Unknown").replace(" ", "")
        entity_id = f"urn:ngsi-ld:WeatherObserved:{city_name}"
        
        now = datetime.utcnow()
        
        # Map fields to NGSI-LD Properties
        temp = Property(value=raw_data["main"]["temp"], unitCode="CEL", observedAt=now)
        humidity = Property(value=raw_data["main"]["humidity"], unitCode="P1", observedAt=now) # P1 = Percent
        pressure = Property(value=raw_data["main"]["pressure"], unitCode="A97", observedAt=now) # A97 = hPa
        
        # GeoProperty
        lon = raw_data["coord"]["lon"]
        lat = raw_data["coord"]["lat"]
        location = GeoProperty(
            value={
                "type": "Point",
                "coordinates": [lon, lat]
            }
        )

        return Entity(
            id=entity_id,
            type="WeatherObserved",
            location=location,
            at_context=["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"],
            # Dynamic attributes via extra fields
            temperature=temp,
            relativeHumidity=humidity,
            atmosphericPressure=pressure,
            weatherType=Property(value=raw_data["weather"][0]["main"], observedAt=now)
        )

