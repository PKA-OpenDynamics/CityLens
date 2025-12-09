# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Admin Analytics & Reporting API
Advanced analytics, comparisons, trends, and data export functionality
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, cast, Float
import io
import csv
import json

from app.api.deps import get_db, get_current_admin
from app.schemas.user import UserProfile

router = APIRouter()


@router.get("/trends/weather", response_model=Dict[str, Any])
async def get_weather_trends(
    days: int = Query(default=30, ge=1, le=365),
    district: Optional[str] = Query(default=None),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get weather trends over time
    Analyze temperature, humidity, precipitation patterns
    """
    try:
        from app.models.db_models import WeatherObserved
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(
            func.date(WeatherObserved.dateObserved).label("date"),
            func.avg(WeatherObserved.temperature).label("avg_temp"),
            func.min(WeatherObserved.temperature).label("min_temp"),
            func.max(WeatherObserved.temperature).label("max_temp"),
            func.avg(WeatherObserved.relativeHumidity).label("avg_humidity"),
            func.sum(WeatherObserved.precipitation).label("total_precipitation"),
            func.count(WeatherObserved.id).label("observations")
        ).filter(WeatherObserved.dateObserved >= start_date)
        
        if district:
            query = query.filter(WeatherObserved.address.ilike(f"%{district}%"))
        
        results = query.group_by(func.date(WeatherObserved.dateObserved)).order_by(
            func.date(WeatherObserved.dateObserved)
        ).all()
        
        return {
            "period": f"last_{days}_days",
            "district": district or "all",
            "data": [
                {
                    "date": r.date.isoformat(),
                    "temperature": {
                        "average": float(r.avg_temp) if r.avg_temp else None,
                        "min": float(r.min_temp) if r.min_temp else None,
                        "max": float(r.max_temp) if r.max_temp else None
                    },
                    "humidity": float(r.avg_humidity) if r.avg_humidity else None,
                    "precipitation": float(r.total_precipitation) if r.total_precipitation else 0,
                    "observations": r.observations
                } for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch weather trends: {str(e)}"
        )


@router.get("/trends/air-quality", response_model=Dict[str, Any])
async def get_air_quality_trends(
    days: int = Query(default=30, ge=1, le=365),
    district: Optional[str] = Query(default=None),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get air quality trends over time
    Analyze AQI, PM2.5, PM10, pollutants patterns
    """
    try:
        from app.models.db_models import AirQualityObserved
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(
            func.date(AirQualityObserved.dateObserved).label("date"),
            func.avg(AirQualityObserved.aqi).label("avg_aqi"),
            func.max(AirQualityObserved.aqi).label("max_aqi"),
            func.avg(AirQualityObserved.pm25).label("avg_pm25"),
            func.avg(AirQualityObserved.pm10).label("avg_pm10"),
            func.avg(AirQualityObserved.co).label("avg_co"),
            func.avg(AirQualityObserved.no2).label("avg_no2"),
            func.count(AirQualityObserved.id).label("observations")
        ).filter(AirQualityObserved.dateObserved >= start_date)
        
        if district:
            query = query.filter(AirQualityObserved.address.ilike(f"%{district}%"))
        
        results = query.group_by(func.date(AirQualityObserved.dateObserved)).order_by(
            func.date(AirQualityObserved.dateObserved)
        ).all()
        
        # Calculate air quality categories distribution
        category_query = db.query(
            AirQualityObserved.airQualityIndex,
            func.count(AirQualityObserved.id).label("count")
        ).filter(AirQualityObserved.dateObserved >= start_date)
        
        if district:
            category_query = category_query.filter(AirQualityObserved.address.ilike(f"%{district}%"))
        
        categories = category_query.group_by(AirQualityObserved.airQualityIndex).all()
        
        return {
            "period": f"last_{days}_days",
            "district": district or "all",
            "data": [
                {
                    "date": r.date.isoformat(),
                    "aqi": {
                        "average": float(r.avg_aqi) if r.avg_aqi else None,
                        "max": float(r.max_aqi) if r.max_aqi else None
                    },
                    "pollutants": {
                        "pm25": float(r.avg_pm25) if r.avg_pm25 else None,
                        "pm10": float(r.avg_pm10) if r.avg_pm10 else None,
                        "co": float(r.avg_co) if r.avg_co else None,
                        "no2": float(r.avg_no2) if r.avg_no2 else None
                    },
                    "observations": r.observations
                } for r in results
            ],
            "category_distribution": {
                cat.airQualityIndex: cat.count for cat in categories if cat.airQualityIndex
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch air quality trends: {str(e)}"
        )


@router.get("/trends/traffic", response_model=Dict[str, Any])
async def get_traffic_trends(
    days: int = Query(default=7, ge=1, le=90),
    location: Optional[str] = Query(default=None),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get traffic trends over time
    Analyze congestion patterns, vehicle speed, intensity by hour
    """
    try:
        from app.models.db_models import TrafficFlowObserved
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily aggregation
        daily_query = db.query(
            func.date(TrafficFlowObserved.dateObserved).label("date"),
            func.avg(TrafficFlowObserved.intensity).label("avg_intensity"),
            func.avg(TrafficFlowObserved.averageVehicleSpeed).label("avg_speed"),
            func.avg(TrafficFlowObserved.averageHeadwayTime).label("avg_headway"),
            func.count(TrafficFlowObserved.id).label("observations")
        ).filter(TrafficFlowObserved.dateObserved >= start_date)
        
        if location:
            daily_query = daily_query.filter(TrafficFlowObserved.location.ilike(f"%{location}%"))
        
        daily_results = daily_query.group_by(func.date(TrafficFlowObserved.dateObserved)).order_by(
            func.date(TrafficFlowObserved.dateObserved)
        ).all()
        
        # Hourly pattern (average across all days)
        hourly_query = db.query(
            func.extract('hour', TrafficFlowObserved.dateObserved).label("hour"),
            func.avg(TrafficFlowObserved.intensity).label("avg_intensity"),
            func.avg(TrafficFlowObserved.averageVehicleSpeed).label("avg_speed"),
            func.count(TrafficFlowObserved.id).label("observations")
        ).filter(TrafficFlowObserved.dateObserved >= start_date)
        
        if location:
            hourly_query = hourly_query.filter(TrafficFlowObserved.location.ilike(f"%{location}%"))
        
        hourly_results = hourly_query.group_by(
            func.extract('hour', TrafficFlowObserved.dateObserved)
        ).order_by(
            func.extract('hour', TrafficFlowObserved.dateObserved)
        ).all()
        
        return {
            "period": f"last_{days}_days",
            "location": location or "all",
            "daily_trends": [
                {
                    "date": r.date.isoformat(),
                    "intensity": float(r.avg_intensity) if r.avg_intensity else None,
                    "average_speed": float(r.avg_speed) if r.avg_speed else None,
                    "average_headway": float(r.avg_headway) if r.avg_headway else None,
                    "observations": r.observations
                } for r in daily_results
            ],
            "hourly_pattern": [
                {
                    "hour": int(r.hour),
                    "intensity": float(r.avg_intensity) if r.avg_intensity else None,
                    "average_speed": float(r.avg_speed) if r.avg_speed else None,
                    "observations": r.observations
                } for r in hourly_results
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch traffic trends: {str(e)}"
        )


@router.get("/compare/districts", response_model=Dict[str, Any])
async def compare_districts(
    metric: str = Query(..., regex="^(temperature|aqi|traffic_intensity)$"),
    days: int = Query(default=7, ge=1, le=90),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Compare metrics across different districts
    Useful for identifying problem areas and resource allocation
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        if metric == "temperature":
            from app.models.db_models import WeatherObserved
            
            results = db.query(
                WeatherObserved.address,
                func.avg(WeatherObserved.temperature).label("avg_value"),
                func.min(WeatherObserved.temperature).label("min_value"),
                func.max(WeatherObserved.temperature).label("max_value"),
                func.count(WeatherObserved.id).label("count")
            ).filter(
                WeatherObserved.dateObserved >= start_date
            ).group_by(WeatherObserved.address).order_by(
                func.avg(WeatherObserved.temperature).desc()
            ).all()
            
        elif metric == "aqi":
            from app.models.db_models import AirQualityObserved
            
            results = db.query(
                AirQualityObserved.address,
                func.avg(AirQualityObserved.aqi).label("avg_value"),
                func.min(AirQualityObserved.aqi).label("min_value"),
                func.max(AirQualityObserved.aqi).label("max_value"),
                func.count(AirQualityObserved.id).label("count")
            ).filter(
                AirQualityObserved.dateObserved >= start_date
            ).group_by(AirQualityObserved.address).order_by(
                func.avg(AirQualityObserved.aqi).desc()
            ).all()
            
        else:  # traffic_intensity
            from app.models.db_models import TrafficFlowObserved
            
            results = db.query(
                TrafficFlowObserved.location,
                func.avg(TrafficFlowObserved.intensity).label("avg_value"),
                func.min(TrafficFlowObserved.intensity).label("min_value"),
                func.max(TrafficFlowObserved.intensity).label("max_value"),
                func.count(TrafficFlowObserved.id).label("count")
            ).filter(
                TrafficFlowObserved.dateObserved >= start_date
            ).group_by(TrafficFlowObserved.location).order_by(
                func.avg(TrafficFlowObserved.intensity).desc()
            ).all()
        
        return {
            "metric": metric,
            "period": f"last_{days}_days",
            "comparisons": [
                {
                    "location": r.address if metric != "traffic_intensity" else r.location,
                    "average": float(r.avg_value) if r.avg_value else None,
                    "min": float(r.min_value) if r.min_value else None,
                    "max": float(r.max_value) if r.max_value else None,
                    "data_points": r.count
                } for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare districts: {str(e)}"
        )


@router.get("/export/csv", response_class=StreamingResponse)
async def export_data_csv(
    entity_type: str = Query(..., regex="^(weather|air_quality|traffic|parking|civic_issues)$"),
    days: int = Query(default=7, ge=1, le=90),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Export entity data as CSV file
    Supports all major entity types with NGSI-LD compatibility
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        output = io.StringIO()
        
        if entity_type == "weather":
            from app.models.db_models import WeatherObserved
            
            writer = csv.writer(output)
            writer.writerow([
                "ID", "Date Observed", "Location", "Address", 
                "Temperature (°C)", "Humidity (%)", "Precipitation (mm)",
                "Weather Type", "Wind Speed (m/s)", "Atmospheric Pressure (hPa)"
            ])
            
            data = db.query(WeatherObserved).filter(
                WeatherObserved.dateObserved >= start_date
            ).order_by(WeatherObserved.dateObserved.desc()).all()
            
            for item in data:
                writer.writerow([
                    item.id, item.dateObserved.isoformat(), item.location, item.address,
                    item.temperature, item.relativeHumidity, item.precipitation,
                    item.weatherType, item.windSpeed, item.atmosphericPressure
                ])
                
        elif entity_type == "air_quality":
            from app.models.db_models import AirQualityObserved
            
            writer = csv.writer(output)
            writer.writerow([
                "ID", "Date Observed", "Location", "Address",
                "AQI", "Air Quality Category", "PM2.5", "PM10",
                "CO", "NO2", "SO2", "O3"
            ])
            
            data = db.query(AirQualityObserved).filter(
                AirQualityObserved.dateObserved >= start_date
            ).order_by(AirQualityObserved.dateObserved.desc()).all()
            
            for item in data:
                writer.writerow([
                    item.id, item.dateObserved.isoformat(), item.location, item.address,
                    item.aqi, item.airQualityIndex, item.pm25, item.pm10,
                    item.co, item.no2, item.so2, item.o3
                ])
                
        elif entity_type == "traffic":
            from app.models.db_models import TrafficFlowObserved
            
            writer = csv.writer(output)
            writer.writerow([
                "ID", "Date Observed", "Location", "Lane ID",
                "Intensity", "Average Vehicle Speed (km/h)", 
                "Average Vehicle Length (m)", "Congestion Level",
                "Average Headway Time (s)", "Average Gap (m)"
            ])
            
            data = db.query(TrafficFlowObserved).filter(
                TrafficFlowObserved.dateObserved >= start_date
            ).order_by(TrafficFlowObserved.dateObserved.desc()).all()
            
            for item in data:
                writer.writerow([
                    item.id, item.dateObserved.isoformat(), item.location, item.laneId,
                    item.intensity, item.averageVehicleSpeed,
                    item.averageVehicleLength, item.congestionLevel,
                    item.averageHeadwayTime, item.averageGapDistance
                ])
                
        elif entity_type == "civic_issues":
            from app.models.db_models import CivicIssueTracking
            
            writer = csv.writer(output)
            writer.writerow([
                "ID", "Title", "Description", "Category", "Sub-category",
                "Status", "Priority", "Location", "Address",
                "Date Created", "Date Updated", "Resolution Notes"
            ])
            
            data = db.query(CivicIssueTracking).filter(
                CivicIssueTracking.dateCreated >= start_date
            ).order_by(CivicIssueTracking.dateCreated.desc()).all()
            
            for item in data:
                writer.writerow([
                    item.id, item.title, item.description, item.category, item.subCategory,
                    item.status, item.priority, item.location, item.address,
                    item.dateCreated.isoformat(), item.dateUpdated.isoformat() if item.dateUpdated else "",
                    item.resolutionNotes or ""
                ])
        
        output.seek(0)
        filename = f"citylens_{entity_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.get("/statistics/summary", response_model=Dict[str, Any])
async def get_statistics_summary(
    days: int = Query(default=30, ge=1, le=365),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics summary
    Useful for generating reports and executive dashboards
    """
    try:
        from app.models.db_models import WeatherObserved
        from app.models.db_models import AirQualityObserved
        from app.models.db_models import TrafficFlowObserved
        from app.models.db_models import CivicIssueTracking
        from app.models.db_models import ParkingSpot
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Weather statistics
        weather_stats = db.query(
            func.count(WeatherObserved.id).label("count"),
            func.avg(WeatherObserved.temperature).label("avg_temp"),
            func.min(WeatherObserved.temperature).label("min_temp"),
            func.max(WeatherObserved.temperature).label("max_temp"),
            func.sum(WeatherObserved.precipitation).label("total_precip")
        ).filter(WeatherObserved.dateObserved >= start_date).first()
        
        # Air quality statistics
        aqi_stats = db.query(
            func.count(AirQualityObserved.id).label("count"),
            func.avg(AirQualityObserved.aqi).label("avg_aqi"),
            func.max(AirQualityObserved.aqi).label("max_aqi")
        ).filter(AirQualityObserved.dateObserved >= start_date).first()
        
        # Count dangerous AQI days (>150)
        dangerous_aqi_days = db.query(
            func.count(func.distinct(func.date(AirQualityObserved.dateObserved)))
        ).filter(
            and_(
                AirQualityObserved.dateObserved >= start_date,
                AirQualityObserved.aqi > 150
            )
        ).scalar()
        
        # Traffic statistics
        traffic_stats = db.query(
            func.count(TrafficFlowObserved.id).label("count"),
            func.avg(TrafficFlowObserved.intensity).label("avg_intensity"),
            func.avg(TrafficFlowObserved.averageVehicleSpeed).label("avg_speed")
        ).filter(TrafficFlowObserved.dateObserved >= start_date).first()
        
        # Civic issues statistics
        civic_stats = db.query(
            func.count(CivicIssueTracking.id).label("total"),
            func.sum(case((CivicIssueTracking.status == "open", 1), else_=0)).label("open_count"),
            func.sum(case((CivicIssueTracking.status == "closed", 1), else_=0)).label("closed_count")
        ).filter(CivicIssueTracking.dateCreated >= start_date).first()
        
        # Calculate resolution rate
        resolution_rate = 0
        if civic_stats and civic_stats.total > 0:
            resolution_rate = (civic_stats.closed_count or 0) / civic_stats.total * 100
        
        # Parking statistics
        parking_total = db.query(func.count(ParkingSpot.id)).scalar()
        parking_available = db.query(func.count(ParkingSpot.id)).filter(
            ParkingSpot.status == "free"
        ).scalar()
        
        return {
            "period": f"last_{days}_days",
            "generated_at": datetime.utcnow().isoformat(),
            "weather": {
                "observations": weather_stats.count if weather_stats else 0,
                "average_temperature": float(weather_stats.avg_temp) if weather_stats and weather_stats.avg_temp else None,
                "temperature_range": {
                    "min": float(weather_stats.min_temp) if weather_stats and weather_stats.min_temp else None,
                    "max": float(weather_stats.max_temp) if weather_stats and weather_stats.max_temp else None
                },
                "total_precipitation": float(weather_stats.total_precip) if weather_stats and weather_stats.total_precip else 0
            },
            "air_quality": {
                "observations": aqi_stats.count if aqi_stats else 0,
                "average_aqi": float(aqi_stats.avg_aqi) if aqi_stats and aqi_stats.avg_aqi else None,
                "max_aqi": float(aqi_stats.max_aqi) if aqi_stats and aqi_stats.max_aqi else None,
                "dangerous_days": dangerous_aqi_days
            },
            "traffic": {
                "observations": traffic_stats.count if traffic_stats else 0,
                "average_intensity": float(traffic_stats.avg_intensity) if traffic_stats and traffic_stats.avg_intensity else None,
                "average_speed": float(traffic_stats.avg_speed) if traffic_stats and traffic_stats.avg_speed else None
            },
            "civic_issues": {
                "total": civic_stats.total if civic_stats else 0,
                "open": civic_stats.open_count if civic_stats else 0,
                "closed": civic_stats.closed_count if civic_stats else 0,
                "resolution_rate": round(resolution_rate, 2)
            },
            "parking": {
                "total_spots": parking_total,
                "available": parking_available,
                "occupied": parking_total - (parking_available or 0),
                "occupancy_rate": round((parking_total - (parking_available or 0)) / parking_total * 100, 2) if parking_total > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate statistics summary: {str(e)}"
        )


# Helper function for case statement (SQLAlchemy)
from sqlalchemy import case
