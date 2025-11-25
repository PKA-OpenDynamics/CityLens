#!/usr/bin/env python3
# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Fetch external data từ WAQI (Air Quality) và OpenWeatherMap
Chạy: python scripts/fetch_external_data.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from sqlalchemy.orm import Session
from app.db.postgres import SessionLocal
from app.models.environment import EnvironmentalData
from datetime import datetime

# API Keys (đọc từ environment)
WAQI_API_KEY = os.getenv("WAQI_API_KEY", "demo")  # demo key cho testing
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Ho Chi Minh City coordinates
HCMC_LAT = 10.8231
HCMC_LON = 106.6297


def fetch_air_quality():
    """Fetch AQI data từ WAQI"""
    try:
        url = f"https://api.waqi.info/feed/geo:{HCMC_LAT};{HCMC_LON}/?token={WAQI_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "ok":
            aqi_data = data.get("data", {})
            aqi_value = aqi_data.get("aqi")
            
            print(f"✓ AQI: {aqi_value} at {aqi_data.get('city', {}).get('name', 'Unknown')}")
            
            # Save to database
            db: Session = SessionLocal()
            env_data = EnvironmentalData(
                district_id=None,  # Citywide data
                data_type="air_quality",
                value=float(aqi_value) if aqi_value else 0,
                unit="AQI",
                measured_at=datetime.utcnow(),
                source="WAQI",
                properties={
                    "pm25": aqi_data.get("iaqi", {}).get("pm25", {}).get("v"),
                    "pm10": aqi_data.get("iaqi", {}).get("pm10", {}).get("v"),
                    "no2": aqi_data.get("iaqi", {}).get("no2", {}).get("v"),
                    "station": aqi_data.get("city", {}).get("name"),
                    "dominentpol": aqi_data.get("dominentpol")
                }
            )
            db.add(env_data)
            db.commit()
            db.close()
            
            return aqi_value
        else:
            print(f"❌ WAQI API error: {data.get('message')}")
            return None
    except Exception as e:
        print(f"❌ Error fetching AQI: {e}")
        return None


def fetch_weather():
    """Fetch weather data từ OpenWeatherMap"""
    if not OPENWEATHER_API_KEY:
        print("⚠️ OpenWeatherMap API key not set. Skipping weather fetch.")
        return None
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={HCMC_LAT}&lon={HCMC_LON}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        temp = data.get("main", {}).get("temp")
        humidity = data.get("main", {}).get("humidity")
        weather_desc = data.get("weather", [{}])[0].get("description")
        
        print(f"✓ Weather: {temp}°C, {humidity}% humidity, {weather_desc}")
        
        # Save temperature
        db: Session = SessionLocal()
        temp_data = EnvironmentalData(
            district_id=None,
            data_type="weather",
            value=float(temp) if temp else 0,
            unit="°C",
            measured_at=datetime.utcnow(),
            source="OpenWeatherMap",
            properties={
                "humidity": humidity,
                "description": weather_desc,
                "pressure": data.get("main", {}).get("pressure"),
                "wind_speed": data.get("wind", {}).get("speed")
            }
        )
        db.add(temp_data)
        db.commit()
        db.close()
        
        return temp
    except Exception as e:
        print(f"❌ Error fetching weather: {e}")
        return None


if __name__ == "__main__":
    print("🌍 Fetching external data for Ho Chi Minh City...\n")
    
    print("1. Fetching Air Quality Index (AQI)...")
    aqi = fetch_air_quality()
    
    print("\n2. Fetching Weather data...")
    temp = fetch_weather()
    
    print("\n✅ External data fetch completed!")
    print(f"   AQI: {aqi if aqi else 'N/A'}")
    print(f"   Temperature: {temp if temp else 'N/A'}°C")
    
    print("\n💡 Tip: Set API keys in .env:")
    print("   WAQI_API_KEY=your_key_here")
    print("   OPENWEATHER_API_KEY=your_key_here")
