# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Admin Dashboard API Endpoints - Simplified Version
Provides statistics and monitoring using EntityDB generic model
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, select, cast, Float
from sqlalchemy.dialects.postgresql import JSONB

from app.api.deps import get_db, get_current_admin
from app.schemas.user import UserProfile
from app.db.mongodb import MongoDB
from app.models.db_models import EntityDB

router = APIRouter()
mongodb = MongoDB()


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview with real-time statistics"""
    try:
        # MongoDB User Statistics
        mongo_db = mongodb.get_db()
        users_collection = mongo_db.users
        
        total_users = await users_collection.count_documents({})
        active_users = await users_collection.count_documents({"status": "approved"})
        pending_users = await users_collection.count_documents({"status": "pending"})
        suspended_users = await users_collection.count_documents({"status": "suspended"})
        
        # Count by role
        role_pipeline = [{"$group": {"_id": "$role", "count": {"$sum": 1}}}]
        roles_cursor = users_collection.aggregate(role_pipeline)
        roles_data = await roles_cursor.to_list(length=10)
        users_by_role = {item["_id"]: item["count"] for item in roles_data}
        
        # Entity Statistics from EntityDB
        last_24h = datetime.utcnow() - timedelta(hours=24)
        last_7d = datetime.utcnow() - timedelta(days=7)
        
        # Weather entities
        weather_total = db.query(func.count(EntityDB.id)).filter(
            EntityDB.type == "WeatherObserved"
        ).scalar() or 0
        
        weather_recent = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "WeatherObserved",
                EntityDB.modified_at >= last_24h
            )
        ).scalar() or 0
        
        weather_7d = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "WeatherObserved",
                EntityDB.modified_at >= last_7d
            )
        ).scalar() or 0
        
        # Air Quality entities
        aqi_total = db.query(func.count(EntityDB.id)).filter(
            EntityDB.type == "AirQualityObserved"
        ).scalar() or 0
        
        aqi_recent = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "AirQualityObserved",
                EntityDB.modified_at >= last_24h
            )
        ).scalar() or 0
        
        aqi_7d = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "AirQualityObserved",
                EntityDB.modified_at >= last_7d
            )
        ).scalar() or 0
        
        # Traffic entities
        traffic_total = db.query(func.count(EntityDB.id)).filter(
            EntityDB.type == "TrafficFlowObserved"
        ).scalar() or 0
        
        traffic_recent = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "TrafficFlowObserved",
                EntityDB.modified_at >= last_24h
            )
        ).scalar() or 0
        
        traffic_7d = db.query(func.count(EntityDB.id)).filter(
            and_(
                EntityDB.type == "TrafficFlowObserved",
                EntityDB.modified_at >= last_7d
            )
        ).scalar() or 0
        
        # Parking entities
        parking_total = db.query(func.count(EntityDB.id)).filter(
            EntityDB.type == "ParkingSpot"
        ).scalar() or 0
        
        # Civic Issue entities
        civic_total = db.query(func.count(EntityDB.id)).filter(
            EntityDB.type == "CivicIssueTracking"
        ).scalar() or 0
        
        # System Health
        db_status = "healthy"
        try:
            db.execute(select(1))
        except:
            db_status = "error"
            
        mongodb_status = "healthy"
        try:
            await users_collection.find_one({})
        except:
            mongodb_status = "error"
        
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
                    "total": weather_total,
                    "last_24h": weather_recent,
                    "last_7d": weather_7d
                },
                "air_quality": {
                    "total": aqi_total,
                    "last_24h": aqi_recent,
                    "last_7d": aqi_7d
                },
                "traffic": {
                    "total": traffic_total,
                    "last_24h": traffic_recent,
                    "last_7d": traffic_7d
                },
                "parking": {
                    "total": parking_total,
                    "available": 0,
                    "occupied": 0
                },
                "civic_issues": {
                    "total": civic_total,
                    "open": 0,
                    "closed": 0
                }
            },
            "alert_statistics": {
                "critical": 0,
                "high_priority_open": 0
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


@router.get("/real-time-metrics", response_model=Dict[str, Any])
async def get_real_time_metrics(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get latest real-time metrics for monitoring"""
    try:
        # Get latest entities by type
        latest_weather = db.query(EntityDB).filter(
            EntityDB.type == "WeatherObserved"
        ).order_by(EntityDB.modified_at.desc()).first()
        
        latest_aqi = db.query(EntityDB).filter(
            EntityDB.type == "AirQualityObserved"
        ).order_by(EntityDB.modified_at.desc()).first()
        
        latest_traffic = db.query(EntityDB).filter(
            EntityDB.type == "TrafficFlowObserved"
        ).order_by(EntityDB.modified_at.desc()).first()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "weather": {
                "latest": {
                    "temperature": latest_weather.data.get("temperature", {}).get("value") if latest_weather else None,
                    "humidity": latest_weather.data.get("relativeHumidity", {}).get("value") if latest_weather else None,
                    "description": latest_weather.data.get("weatherType", {}).get("value") if latest_weather else None,
                    "observed_at": latest_weather.modified_at.isoformat() if latest_weather and latest_weather.modified_at else None
                },
                "hourly_average": {"temperature": None}
            },
            "air_quality": {
                "latest": {
                    "aqi": latest_aqi.data.get("aqi", {}).get("value") if latest_aqi else None,
                    "pm25": latest_aqi.data.get("pm25", {}).get("value") if latest_aqi else None,
                    "pm10": latest_aqi.data.get("pm10", {}).get("value") if latest_aqi else None,
                    "observed_at": latest_aqi.modified_at.isoformat() if latest_aqi and latest_aqi.modified_at else None
                },
                "hourly_average": {"aqi": None}
            },
            "traffic": {
                "latest": {
                    "intensity": latest_traffic.data.get("intensity", {}).get("value") if latest_traffic else None,
                    "average_speed": latest_traffic.data.get("averageVehicleSpeed", {}).get("value") if latest_traffic else None,
                    "observed_at": latest_traffic.modified_at.isoformat() if latest_traffic and latest_traffic.modified_at else None
                },
                "hourly_average": {"intensity": None}
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch real-time metrics: {str(e)}"
        )


@router.get("/entity-counts", response_model=Dict[str, Any])
async def get_entity_counts(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get entity counts by type"""
    try:
        # Count entities by type
        results = db.query(
            EntityDB.type,
            func.count(EntityDB.id).label("count")
        ).group_by(EntityDB.type).all()
        
        counts = {r.type: r.count for r in results}
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "entity_counts": counts,
            "total_entities": sum(counts.values())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch entity counts: {str(e)}"
        )
