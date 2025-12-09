# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Admin Alert & Incident Management API
Real-time monitoring, alert generation, and incident tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from pydantic import BaseModel

from app.api.deps import get_db, get_current_admin, get_current_user
from app.schemas.user import UserProfile

router = APIRouter()


class AlertThreshold(BaseModel):
    """Alert threshold configuration"""
    metric: str
    operator: str  # "gt", "lt", "gte", "lte", "eq"
    value: float
    severity: str  # "info", "warning", "critical"
    enabled: bool = True


class AlertResponse(BaseModel):
    """Alert response model"""
    id: str
    type: str
    severity: str
    title: str
    description: str
    location: Optional[str] = None
    timestamp: datetime
    status: str
    assigned_to: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(
    severity: Optional[str] = Query(default=None, regex="^(info|warning|critical)$"),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all active alerts
    Shows real-time alerts for traffic, air quality, weather, and civic issues
    """
    try:
        alerts = []
        
        # Traffic alerts - High congestion
        from app.models.db_models import TrafficFlowObserved
        
        recent_time = datetime.utcnow() - timedelta(hours=1)
        traffic_alerts = db.query(TrafficFlowObserved).filter(
            and_(
                TrafficFlowObserved.dateObserved >= recent_time,
                TrafficFlowObserved.intensity > 0.7  # High congestion threshold
            )
        ).order_by(TrafficFlowObserved.intensity.desc()).limit(20).all()
        
        for traffic in traffic_alerts:
            alert_severity = "critical" if traffic.intensity > 0.9 else "warning"
            if not severity or severity == alert_severity:
                alerts.append(AlertResponse(
                    id=f"traffic_{traffic.id}",
                    type="traffic_congestion",
                    severity=alert_severity,
                    title=f"Heavy Traffic Detected",
                    description=f"Traffic intensity at {traffic.intensity:.0%} on {traffic.location}",
                    location=traffic.location,
                    timestamp=traffic.dateObserved,
                    status="active",
                    metadata={
                        "intensity": traffic.intensity,
                        "average_speed": traffic.averageVehicleSpeed,
                        "congestion_level": traffic.congestionLevel
                    }
                ))
        
        # Air quality alerts - Poor AQI
        from app.models.db_models import AirQualityObserved
        
        aqi_alerts = db.query(AirQualityObserved).filter(
            and_(
                AirQualityObserved.dateObserved >= recent_time,
                AirQualityObserved.aqi > 100  # Unhealthy threshold
            )
        ).order_by(AirQualityObserved.aqi.desc()).limit(20).all()
        
        for aqi in aqi_alerts:
            alert_severity = "critical" if aqi.aqi > 200 else ("warning" if aqi.aqi > 150 else "info")
            if not severity or severity == alert_severity:
                alerts.append(AlertResponse(
                    id=f"aqi_{aqi.id}",
                    type="air_quality",
                    severity=alert_severity,
                    title=f"Poor Air Quality - AQI {aqi.aqi}",
                    description=f"{aqi.airQualityIndex} air quality detected at {aqi.address}",
                    location=aqi.location,
                    timestamp=aqi.dateObserved,
                    status="active",
                    metadata={
                        "aqi": aqi.aqi,
                        "category": aqi.airQualityIndex,
                        "pm25": aqi.pm25,
                        "pm10": aqi.pm10
                    }
                ))
        
        # Weather alerts - Extreme conditions
        from app.models.db_models import WeatherObserved
        
        weather_alerts = db.query(WeatherObserved).filter(
            and_(
                WeatherObserved.dateObserved >= recent_time,
                or_(
                    WeatherObserved.temperature < 5,  # Very cold
                    WeatherObserved.temperature > 38,  # Very hot
                    WeatherObserved.precipitation > 50  # Heavy rain
                )
            )
        ).order_by(WeatherObserved.dateObserved.desc()).limit(20).all()
        
        for weather in weather_alerts:
            if weather.temperature < 5:
                alert_type = "extreme_cold"
                alert_title = f"Extreme Cold - {weather.temperature}°C"
                alert_severity = "warning"
            elif weather.temperature > 38:
                alert_type = "extreme_heat"
                alert_title = f"Extreme Heat - {weather.temperature}°C"
                alert_severity = "warning"
            else:
                alert_type = "heavy_rain"
                alert_title = f"Heavy Rainfall - {weather.precipitation}mm"
                alert_severity = "warning" if weather.precipitation > 100 else "info"
            
            if not severity or severity == alert_severity:
                alerts.append(AlertResponse(
                    id=f"weather_{weather.id}",
                    type=alert_type,
                    severity=alert_severity,
                    title=alert_title,
                    description=f"Extreme weather conditions at {weather.address}",
                    location=weather.location,
                    timestamp=weather.dateObserved,
                    status="active",
                    metadata={
                        "temperature": weather.temperature,
                        "humidity": weather.relativeHumidity,
                        "precipitation": weather.precipitation,
                        "weather_type": weather.weatherType
                    }
                ))
        
        # Civic issue alerts - High priority open issues
        from app.models.db_models import CivicIssueTracking
        
        civic_alerts = db.query(CivicIssueTracking).filter(
            and_(
                CivicIssueTracking.status.in_(["open", "in_progress"]),
                CivicIssueTracking.priority == "high"
            )
        ).order_by(CivicIssueTracking.dateCreated.desc()).limit(20).all()
        
        for civic in civic_alerts:
            if not severity or severity == "critical":
                alerts.append(AlertResponse(
                    id=f"civic_{civic.id}",
                    type="civic_issue",
                    severity="critical",
                    title=civic.title,
                    description=civic.description or f"High priority {civic.category} issue",
                    location=civic.location,
                    timestamp=civic.dateCreated,
                    status="open",
                    metadata={
                        "category": civic.category,
                        "sub_category": civic.subCategory,
                        "priority": civic.priority,
                        "status": civic.status
                    }
                ))
        
        # Sort by timestamp and limit
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active alerts: {str(e)}"
        )


@router.get("/history", response_model=Dict[str, Any])
async def get_alert_history(
    days: int = Query(default=7, ge=1, le=90),
    alert_type: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None, regex="^(info|warning|critical)$"),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get alert history with statistics
    Useful for trend analysis and reporting
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Count alerts by type and severity
        alert_summary = {
            "period": f"last_{days}_days",
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "total_alerts": 0,
            "by_type": {},
            "by_severity": {
                "info": 0,
                "warning": 0,
                "critical": 0
            },
            "daily_trend": []
        }
        
        from app.models.db_models import TrafficFlowObserved
        from app.models.db_models import AirQualityObserved
        from app.models.db_models import CivicIssueTracking
        
        # Traffic congestion alerts
        traffic_count = db.query(func.count(TrafficFlowObserved.id)).filter(
            and_(
                TrafficFlowObserved.dateObserved >= start_date,
                TrafficFlowObserved.intensity > 0.7
            )
        ).scalar()
        alert_summary["by_type"]["traffic_congestion"] = traffic_count
        alert_summary["total_alerts"] += traffic_count
        alert_summary["by_severity"]["warning"] += traffic_count
        
        # Air quality alerts
        aqi_warning = db.query(func.count(AirQualityObserved.id)).filter(
            and_(
                AirQualityObserved.dateObserved >= start_date,
                AirQualityObserved.aqi > 100,
                AirQualityObserved.aqi <= 200
            )
        ).scalar()
        aqi_critical = db.query(func.count(AirQualityObserved.id)).filter(
            and_(
                AirQualityObserved.dateObserved >= start_date,
                AirQualityObserved.aqi > 200
            )
        ).scalar()
        alert_summary["by_type"]["air_quality"] = aqi_warning + aqi_critical
        alert_summary["total_alerts"] += aqi_warning + aqi_critical
        alert_summary["by_severity"]["warning"] += aqi_warning
        alert_summary["by_severity"]["critical"] += aqi_critical
        
        # Civic issues
        civic_high = db.query(func.count(CivicIssueTracking.id)).filter(
            and_(
                CivicIssueTracking.dateCreated >= start_date,
                CivicIssueTracking.priority == "high"
            )
        ).scalar()
        alert_summary["by_type"]["civic_issue"] = civic_high
        alert_summary["total_alerts"] += civic_high
        alert_summary["by_severity"]["critical"] += civic_high
        
        # Daily trend
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            daily_traffic = db.query(func.count(TrafficFlowObserved.id)).filter(
                and_(
                    TrafficFlowObserved.dateObserved >= date,
                    TrafficFlowObserved.dateObserved < next_date,
                    TrafficFlowObserved.intensity > 0.7
                )
            ).scalar()
            
            daily_aqi = db.query(func.count(AirQualityObserved.id)).filter(
                and_(
                    AirQualityObserved.dateObserved >= date,
                    AirQualityObserved.dateObserved < next_date,
                    AirQualityObserved.aqi > 100
                )
            ).scalar()
            
            daily_civic = db.query(func.count(CivicIssueTracking.id)).filter(
                and_(
                    CivicIssueTracking.dateCreated >= date,
                    CivicIssueTracking.dateCreated < next_date,
                    CivicIssueTracking.priority == "high"
                )
            ).scalar()
            
            alert_summary["daily_trend"].append({
                "date": date.strftime("%Y-%m-%d"),
                "total": daily_traffic + daily_aqi + daily_civic,
                "traffic": daily_traffic,
                "air_quality": daily_aqi,
                "civic_issues": daily_civic
            })
        
        return alert_summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert history: {str(e)}"
        )


@router.post("/acknowledge/{alert_id}", response_model=Dict[str, str])
async def acknowledge_alert(
    alert_id: str,
    notes: Optional[str] = Body(default=None),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert
    Marks the alert as acknowledged by the current user
    """
    try:
        # Parse alert_id (format: "type_id")
        alert_parts = alert_id.split("_", 1)
        if len(alert_parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid alert ID format"
            )
        
        alert_type = alert_parts[0]
        entity_id = alert_parts[1]
        
        # For civic issues, we can actually update the status
        if alert_type == "civic":
            from app.models.db_models import CivicIssueTracking
            
            civic_issue = db.query(CivicIssueTracking).filter(
                CivicIssueTracking.id == entity_id
            ).first()
            
            if not civic_issue:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Civic issue not found"
                )
            
            # Update to in_progress if currently open
            if civic_issue.status == "open":
                civic_issue.status = "in_progress"
                civic_issue.dateUpdated = datetime.utcnow()
                if notes:
                    civic_issue.resolutionNotes = f"[{current_user.full_name}] {notes}"
                db.commit()
        
        # For other types, just log the acknowledgment
        # In a real system, you'd store this in a separate alerts table
        
        return {
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": current_user.email,
            "acknowledged_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge alert: {str(e)}"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_alert_statistics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive alert statistics
    Shows patterns, most affected areas, and trends
    """
    try:
        from app.models.db_models import TrafficFlowObserved
        from app.models.db_models import AirQualityObserved
        from app.models.db_models import CivicIssueTracking
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Most congested locations
        top_congested = db.query(
            TrafficFlowObserved.location,
            func.count(TrafficFlowObserved.id).label("count"),
            func.avg(TrafficFlowObserved.intensity).label("avg_intensity")
        ).filter(
            and_(
                TrafficFlowObserved.dateObserved >= start_date,
                TrafficFlowObserved.intensity > 0.7
            )
        ).group_by(TrafficFlowObserved.location).order_by(
            func.count(TrafficFlowObserved.id).desc()
        ).limit(10).all()
        
        # Worst air quality locations
        worst_aqi = db.query(
            AirQualityObserved.address,
            func.count(AirQualityObserved.id).label("count"),
            func.avg(AirQualityObserved.aqi).label("avg_aqi"),
            func.max(AirQualityObserved.aqi).label("max_aqi")
        ).filter(
            and_(
                AirQualityObserved.dateObserved >= start_date,
                AirQualityObserved.aqi > 100
            )
        ).group_by(AirQualityObserved.address).order_by(
            func.avg(AirQualityObserved.aqi).desc()
        ).limit(10).all()
        
        # Civic issues by category
        civic_by_category = db.query(
            CivicIssueTracking.category,
            func.count(CivicIssueTracking.id).label("count")
        ).filter(
            and_(
                CivicIssueTracking.dateCreated >= start_date,
                CivicIssueTracking.priority == "high"
            )
        ).group_by(CivicIssueTracking.category).all()
        
        # Response time statistics (for civic issues)
        avg_response_time = db.query(
            func.avg(
                func.extract('epoch', CivicIssueTracking.dateUpdated - CivicIssueTracking.dateCreated) / 3600
            ).label("hours")
        ).filter(
            and_(
                CivicIssueTracking.dateCreated >= start_date,
                CivicIssueTracking.dateUpdated.isnot(None),
                CivicIssueTracking.status == "closed"
            )
        ).scalar()
        
        return {
            "period": f"last_{days}_days",
            "top_congested_locations": [
                {
                    "location": r.location,
                    "alert_count": r.count,
                    "avg_intensity": float(r.avg_intensity)
                } for r in top_congested
            ],
            "worst_air_quality_locations": [
                {
                    "location": r.address,
                    "alert_count": r.count,
                    "avg_aqi": float(r.avg_aqi),
                    "max_aqi": float(r.max_aqi)
                } for r in worst_aqi
            ],
            "civic_issues_by_category": {
                r.category: r.count for r in civic_by_category
            },
            "average_response_time_hours": float(avg_response_time) if avg_response_time else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch alert statistics: {str(e)}"
        )


@router.get("/recommendations", response_model=Dict[str, Any])
async def get_alert_recommendations(
    current_user: UserProfile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered recommendations based on current alerts
    Provides actionable insights for city management
    """
    try:
        from app.models.db_models import TrafficFlowObserved
        from app.models.db_models import AirQualityObserved
        from app.models.db_models import CivicIssueTracking
        
        recommendations = []
        recent_time = datetime.utcnow() - timedelta(hours=2)
        
        # Check for recurring traffic congestion
        congested_locations = db.query(
            TrafficFlowObserved.location,
            func.count(TrafficFlowObserved.id).label("count")
        ).filter(
            and_(
                TrafficFlowObserved.dateObserved >= recent_time,
                TrafficFlowObserved.intensity > 0.8
            )
        ).group_by(TrafficFlowObserved.location).having(
            func.count(TrafficFlowObserved.id) > 3
        ).all()
        
        for loc in congested_locations:
            recommendations.append({
                "type": "traffic_management",
                "priority": "high",
                "title": f"Recurring Congestion at {loc.location}",
                "description": f"Detected {loc.count} high congestion events in the last 2 hours",
                "action": "Consider traffic signal optimization or alternative route suggestions",
                "location": loc.location
            })
        
        # Check for sustained poor air quality
        poor_aqi_areas = db.query(
            AirQualityObserved.address,
            func.avg(AirQualityObserved.aqi).label("avg_aqi")
        ).filter(
            AirQualityObserved.dateObserved >= recent_time
        ).group_by(AirQualityObserved.address).having(
            func.avg(AirQualityObserved.aqi) > 150
        ).all()
        
        for area in poor_aqi_areas:
            recommendations.append({
                "type": "air_quality_management",
                "priority": "critical",
                "title": f"Sustained Poor Air Quality in {area.address}",
                "description": f"Average AQI of {area.avg_aqi:.0f} detected",
                "action": "Issue public health advisory and consider traffic restrictions",
                "location": area.address
            })
        
        # Check for unresolved high-priority civic issues
        old_civic_issues = db.query(CivicIssueTracking).filter(
            and_(
                CivicIssueTracking.status == "open",
                CivicIssueTracking.priority == "high",
                CivicIssueTracking.dateCreated < datetime.utcnow() - timedelta(days=3)
            )
        ).count()
        
        if old_civic_issues > 0:
            recommendations.append({
                "type": "civic_issue_management",
                "priority": "high",
                "title": f"{old_civic_issues} High Priority Issues Unresolved",
                "description": f"Issues older than 3 days need attention",
                "action": "Review and assign resources to pending high-priority civic issues",
                "location": "citywide"
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_recommendations": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
