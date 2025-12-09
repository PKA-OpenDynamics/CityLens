# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Admin Dashboard API Endpoints
Provides comprehensive statistics, monitoring, and analytics for city management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.schemas.user import UserProfile
from app.db.mongodb import MongoDB

router = APIRouter()

# Initialize MongoDB
mongodb = MongoDB()


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard overview with real-time statistics
    
    Returns:
    - User statistics (total, active, pending, by role)
    - System health metrics
    - Entity counts from NGSI-LD (weather, air quality, traffic, parking, civic issues)
    - Recent activity summary
    - Alert statistics
    """
    try:
        # Get MongoDB database
        mongo_db = mongodb.get_db()
        users_collection = mongo_db.users
        
        # User Statistics
        total_users = await users_collection.count_documents({})
        active_users = await users_collection.count_documents({"status": "approved"})
        pending_users = await users_collection.count_documents({"status": "pending"})
        suspended_users = await users_collection.count_documents({"status": "suspended"})
        
        # Count by role
        role_pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        roles_cursor = users_collection.aggregate(role_pipeline)
        roles_data = await roles_cursor.to_list(length=10)
        users_by_role = {item["_id"]: item["count"] for item in roles_data}
        
        # Entity Statistics from PostgreSQL (NGSI-LD entities)
        from app.models.db_models import (
            WeatherObserved,
            AirQualityObserved,
            TrafficFlowObserved,
            ParkingSpot,
            CivicIssueTracking
        )
        
        # Get recent data counts (last 24 hours)
        last_24h = datetime.utcnow() - timedelta(hours=24)
        
        weather_count = db.query(func.count(WeatherObserved.id)).scalar()
        weather_recent = db.query(func.count(WeatherObserved.id)).filter(
            WeatherObserved.dateObserved >= last_24h
        ).scalar()
        
        air_quality_count = db.query(func.count(AirQualityObserved.id)).scalar()
        air_quality_recent = db.query(func.count(AirQualityObserved.id)).filter(
            AirQualityObserved.dateObserved >= last_24h
        ).scalar()
        
        traffic_count = db.query(func.count(TrafficFlowObserved.id)).scalar()
        traffic_recent = db.query(func.count(TrafficFlowObserved.id)).filter(
            TrafficFlowObserved.dateObserved >= last_24h
        ).scalar()
        
        parking_count = db.query(func.count(ParkingSpot.id)).scalar()
        parking_available = db.query(func.count(ParkingSpot.id)).filter(
            ParkingSpot.status == "free"
        ).scalar()
        
        civic_issues_count = db.query(func.count(CivicIssueTracking.id)).scalar()
        civic_issues_open = db.query(func.count(CivicIssueTracking.id)).filter(
            CivicIssueTracking.status.in_(["open", "in_progress"])
        ).scalar()
        
        # Alert Statistics (from civic issues as example)
        alerts_critical = db.query(func.count(CivicIssueTracking.id)).filter(
            and_(
                CivicIssueTracking.status.in_(["open", "in_progress"]),
                CivicIssueTracking.priority == "high"
            )
        ).scalar()
        
        # System Health Metrics
        from app.db.postgres import engine
        try:
            # Test database connection
            with engine.connect() as conn:
                db_status = "healthy"
        except Exception:
            db_status = "error"
            
        # Check MongoDB
        try:
            await users_collection.find_one({})
            mongodb_status = "healthy"
        except Exception:
            mongodb_status = "error"
        
        # Recent Activity (last 7 days trend)
        last_7_days = datetime.utcnow() - timedelta(days=7)
        recent_weather = db.query(func.count(WeatherObserved.id)).filter(
            WeatherObserved.dateObserved >= last_7_days
        ).scalar()
        recent_air_quality = db.query(func.count(AirQualityObserved.id)).filter(
            AirQualityObserved.dateObserved >= last_7_days
        ).scalar()
        recent_traffic = db.query(func.count(TrafficFlowObserved.id)).filter(
            TrafficFlowObserved.dateObserved >= last_7_days
        ).scalar()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "user_statistics": {
                "total": total_users,
                "active": active_users,
                "pending": pending_users,
                "suspended": suspended_users,
                "by_role": users_by_role
            },
            "entity_statistics": {
                "weather": {
                    "total": weather_count,
                    "last_24h": weather_recent,
                    "last_7d": recent_weather
                },
                "air_quality": {
                    "total": air_quality_count,
                    "last_24h": air_quality_recent,
                    "last_7d": recent_air_quality
                },
                "traffic": {
                    "total": traffic_count,
                    "last_24h": traffic_recent,
                    "last_7d": recent_traffic
                },
                "parking": {
                    "total": parking_count,
                    "available": parking_available,
                    "occupied": parking_count - (parking_available or 0)
                },
                "civic_issues": {
                    "total": civic_issues_count,
                    "open": civic_issues_open,
                    "closed": civic_issues_count - (civic_issues_open or 0)
                }
            },
            "alert_statistics": {
                "critical": alerts_critical,
                "high_priority_open": civic_issues_open
            },
            "system_health": {
                "database": db_status,
                "mongodb": mongodb_status,
                "status": "healthy" if db_status == "healthy" and mongodb_status == "healthy" else "degraded"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard overview: {str(e)}"
        )


@router.get("/activity-timeline", response_model=Dict[str, Any])
async def get_activity_timeline(
    days: int = Query(default=7, ge=1, le=90),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get activity timeline for the last N days
    Shows data collection trends across all entity types
    """
    try:
        from app.models.db_models import (
            WeatherObserved,
            AirQualityObserved,
            TrafficFlowObserved,
            CivicIssueTracking
        )
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Generate daily buckets
        timeline = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            weather_count = db.query(func.count(WeatherObserved.id)).filter(
                and_(
                    WeatherObserved.dateObserved >= date,
                    WeatherObserved.dateObserved < next_date
                )
            ).scalar()
            
            air_quality_count = db.query(func.count(AirQualityObserved.id)).filter(
                and_(
                    AirQualityObserved.dateObserved >= date,
                    AirQualityObserved.dateObserved < next_date
                )
            ).scalar()
            
            traffic_count = db.query(func.count(TrafficFlowObserved.id)).filter(
                and_(
                    TrafficFlowObserved.dateObserved >= date,
                    TrafficFlowObserved.dateObserved < next_date
                )
            ).scalar()
            
            civic_count = db.query(func.count(CivicIssueTracking.id)).filter(
                and_(
                    CivicIssueTracking.dateCreated >= date,
                    CivicIssueTracking.dateCreated < next_date
                )
            ).scalar()
            
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "weather": weather_count,
                "air_quality": air_quality_count,
                "traffic": traffic_count,
                "civic_issues": civic_count,
                "total": weather_count + air_quality_count + traffic_count + civic_count
            })
        
        return {
            "period": f"last_{days}_days",
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "timeline": timeline
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch activity timeline: {str(e)}"
        )


@router.get("/real-time-metrics", response_model=Dict[str, Any])
async def get_real_time_metrics(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get latest real-time metrics for monitoring
    Shows the most recent data points for each sensor type
    """
    try:
        from app.models.db_models import (
            WeatherObserved,
            AirQualityObserved,
            TrafficFlowObserved
        )
        
        # Get latest weather observation
        latest_weather = db.query(WeatherObserved).order_by(
            WeatherObserved.dateObserved.desc()
        ).first()
        
        # Get latest air quality observation
        latest_air_quality = db.query(AirQualityObserved).order_by(
            AirQualityObserved.dateObserved.desc()
        ).first()
        
        # Get latest traffic observation
        latest_traffic = db.query(TrafficFlowObserved).order_by(
            TrafficFlowObserved.dateObserved.desc()
        ).first()
        
        # Calculate averages for the last hour
        last_hour = datetime.utcnow() - timedelta(hours=1)
        
        avg_temp = db.query(func.avg(WeatherObserved.temperature)).filter(
            WeatherObserved.dateObserved >= last_hour
        ).scalar()
        
        avg_aqi = db.query(func.avg(AirQualityObserved.aqi)).filter(
            AirQualityObserved.dateObserved >= last_hour
        ).scalar()
        
        avg_traffic_intensity = db.query(func.avg(TrafficFlowObserved.intensity)).filter(
            TrafficFlowObserved.dateObserved >= last_hour
        ).scalar()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "weather": {
                "latest": {
                    "temperature": latest_weather.temperature if latest_weather else None,
                    "humidity": latest_weather.relativeHumidity if latest_weather else None,
                    "description": latest_weather.weatherType if latest_weather else None,
                    "observed_at": latest_weather.dateObserved.isoformat() if latest_weather else None
                },
                "hourly_average": {
                    "temperature": float(avg_temp) if avg_temp else None
                }
            },
            "air_quality": {
                "latest": {
                    "aqi": latest_air_quality.aqi if latest_air_quality else None,
                    "pm25": latest_air_quality.pm25 if latest_air_quality else None,
                    "pm10": latest_air_quality.pm10 if latest_air_quality else None,
                    "observed_at": latest_air_quality.dateObserved.isoformat() if latest_air_quality else None
                },
                "hourly_average": {
                    "aqi": float(avg_aqi) if avg_aqi else None
                }
            },
            "traffic": {
                "latest": {
                    "intensity": latest_traffic.intensity if latest_traffic else None,
                    "average_speed": latest_traffic.averageVehicleSpeed if latest_traffic else None,
                    "observed_at": latest_traffic.dateObserved.isoformat() if latest_traffic else None
                },
                "hourly_average": {
                    "intensity": float(avg_traffic_intensity) if avg_traffic_intensity else None
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch real-time metrics: {str(e)}"
        )


@router.get("/top-locations", response_model=Dict[str, Any])
async def get_top_locations(
    limit: int = Query(default=10, ge=1, le=50),
    metric: str = Query(default="traffic", regex="^(traffic|air_quality|civic_issues)$"),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get top locations based on selected metric
    - traffic: Most congested locations
    - air_quality: Worst AQI locations
    - civic_issues: Most reported locations
    """
    try:
        if metric == "traffic":
            from app.models.db_models import TrafficFlowObserved
            
            results = db.query(
                TrafficFlowObserved.location,
                func.avg(TrafficFlowObserved.intensity).label("avg_intensity"),
                func.count(TrafficFlowObserved.id).label("count")
            ).group_by(
                TrafficFlowObserved.location
            ).order_by(
                func.avg(TrafficFlowObserved.intensity).desc()
            ).limit(limit).all()
            
            return {
                "metric": "traffic_intensity",
                "locations": [
                    {
                        "location": r.location,
                        "value": float(r.avg_intensity),
                        "data_points": r.count
                    } for r in results
                ]
            }
            
        elif metric == "air_quality":
            from app.models.db_models import AirQualityObserved
            
            results = db.query(
                AirQualityObserved.location,
                func.avg(AirQualityObserved.aqi).label("avg_aqi"),
                func.count(AirQualityObserved.id).label("count")
            ).group_by(
                AirQualityObserved.location
            ).order_by(
                func.avg(AirQualityObserved.aqi).desc()
            ).limit(limit).all()
            
            return {
                "metric": "air_quality_index",
                "locations": [
                    {
                        "location": r.location,
                        "value": float(r.avg_aqi),
                        "data_points": r.count
                    } for r in results
                ]
            }
            
        else:  # civic_issues
            from app.models.db_models import CivicIssueTracking
            
            results = db.query(
                CivicIssueTracking.location,
                func.count(CivicIssueTracking.id).label("count")
            ).filter(
                CivicIssueTracking.status.in_(["open", "in_progress"])
            ).group_by(
                CivicIssueTracking.location
            ).order_by(
                func.count(CivicIssueTracking.id).desc()
            ).limit(limit).all()
            
            return {
                "metric": "civic_issues_count",
                "locations": [
                    {
                        "location": r.location,
                        "value": r.count,
                        "data_points": r.count
                    } for r in results
                ]
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top locations: {str(e)}"
        )
