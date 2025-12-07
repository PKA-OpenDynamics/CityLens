# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Statistics Service - Analytics and aggregation for dashboard
Provides overview stats, heatmaps, trends, performance metrics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, extract
from geoalchemy2.functions import ST_Distance, ST_GeomFromText

from app.models.report import Report, ReportStatus, ReportPriority
from app.models.assignment import ReportAssignment, Department
from app.models.user import User


class StatisticsService:
    """Service for generating statistics and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # OVERVIEW STATISTICS
    # ========================================================================
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get high-level overview statistics
        
        Returns:
            - total_reports
            - reports_by_status
            - resolution_rate
            - avg_resolution_time (hours)
            - active_users_30d
            - reports_today
            - reports_this_week
            - reports_this_month
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Total reports
        total_reports = self.db.query(func.count(Report.id)).scalar()
        
        # Reports by status
        status_counts = (
            self.db.query(Report.status, func.count(Report.id))
            .group_by(Report.status)
            .all()
        )
        reports_by_status = {status.value: count for status, count in status_counts}
        
        # Resolution rate
        total_closed = self.db.query(func.count(Report.id)).filter(
            Report.status.in_([ReportStatus.RESOLVED, ReportStatus.REJECTED])
        ).scalar()
        resolution_rate = (total_closed / total_reports * 100) if total_reports > 0 else 0
        
        # Average resolution time (for resolved reports)
        resolved_reports = self.db.query(Report).filter(
            Report.status == ReportStatus.RESOLVED,
            Report.resolved_at.isnot(None)
        ).all()
        
        if resolved_reports:
            total_hours = sum([
                (r.resolved_at - r.created_at).total_seconds() / 3600
                for r in resolved_reports
            ])
            avg_resolution_time = total_hours / len(resolved_reports)
        else:
            avg_resolution_time = 0
        
        # Active users (created report in last 30 days)
        active_users = (
            self.db.query(func.count(func.distinct(Report.user_id)))
            .filter(Report.created_at >= month_start)
            .scalar()
        )
        
        # Reports by time period
        reports_today = self.db.query(func.count(Report.id)).filter(
            Report.created_at >= today_start
        ).scalar()
        
        reports_this_week = self.db.query(func.count(Report.id)).filter(
            Report.created_at >= week_start
        ).scalar()
        
        reports_this_month = self.db.query(func.count(Report.id)).filter(
            Report.created_at >= month_start
        ).scalar()
        
        return {
            "total_reports": total_reports,
            "reports_by_status": reports_by_status,
            "resolution_rate": round(resolution_rate, 2),
            "avg_resolution_time_hours": round(avg_resolution_time, 2),
            "active_users_30d": active_users,
            "reports_today": reports_today,
            "reports_this_week": reports_this_week,
            "reports_this_month": reports_this_month,
            "timestamp": now.isoformat()
        }
    
    # ========================================================================
    # CATEGORY STATISTICS
    # ========================================================================
    
    def get_category_distribution(self) -> Dict[str, Any]:
        """
        Get report distribution by category
        
        Returns list of categories with counts and percentages
        """
        total = self.db.query(func.count(Report.id)).scalar()
        
        category_counts = (
            self.db.query(
                Report.category,
                func.count(Report.id).label('count')
            )
            .group_by(Report.category)
            .order_by(func.count(Report.id).desc())
            .all()
        )
        
        categories = []
        for category, count in category_counts:
            categories.append({
                "category": category,
                "count": count,
                "percentage": round((count / total * 100) if total > 0 else 0, 2)
            })
        
        return {
            "total": total,
            "categories": categories
        }
    
    # ========================================================================
    # GEOGRAPHIC STATISTICS
    # ========================================================================
    
    def get_heatmap_data(
        self,
        bounds: Optional[Dict[str, float]] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get heatmap data for map visualization
        
        Args:
            bounds: Geographic bounds {north, south, east, west}
            status: Filter by status
            category: Filter by category
            days: Number of days to include (default 30)
            
        Returns:
            List of points with coordinates and intensity
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            Report.id,
            func.ST_X(Report.location).label('lon'),
            func.ST_Y(Report.location).label('lat'),
            Report.status,
            Report.category,
            Report.priority,
            Report.upvotes
        ).filter(
            Report.created_at >= cutoff_date
        )
        
        # Apply filters
        if status:
            query = query.filter(Report.status == status)
        if category:
            query = query.filter(Report.category == category)
        
        # Apply geographic bounds
        if bounds:
            query = query.filter(
                and_(
                    func.ST_Y(Report.location) >= bounds['south'],
                    func.ST_Y(Report.location) <= bounds['north'],
                    func.ST_X(Report.location) >= bounds['west'],
                    func.ST_X(Report.location) <= bounds['east']
                )
            )
        
        results = query.all()
        
        # Build heatmap points
        points = []
        for r in results:
            # Calculate intensity based on priority and engagement
            intensity = 1.0
            if r.priority == ReportPriority.HIGH:
                intensity = 1.5
            elif r.priority == ReportPriority.URGENT:
                intensity = 2.0
            
            # Add engagement bonus
            intensity += min(r.upvotes * 0.1, 1.0)
            
            points.append({
                "id": r.id,
                "lat": r.lat,
                "lon": r.lon,
                "intensity": intensity,
                "status": r.status.value if r.status else None,
                "category": r.category
            })
        
        return points
    
    # ========================================================================
    # TIME SERIES STATISTICS
    # ========================================================================
    
    def get_time_series(
        self,
        days: int = 30,
        group_by: str = "day"  # day, week, month
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for trends
        
        Args:
            days: Number of days to include
            group_by: Grouping interval (day, week, month)
            
        Returns:
            List of data points with date and counts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        if group_by == "day":
            date_trunc = func.date_trunc('day', Report.created_at)
        elif group_by == "week":
            date_trunc = func.date_trunc('week', Report.created_at)
        else:  # month
            date_trunc = func.date_trunc('month', Report.created_at)
        
        results = (
            self.db.query(
                date_trunc.label('date'),
                func.count(Report.id).label('total'),
                func.sum(case((Report.status == ReportStatus.RESOLVED, 1), else_=0)).label('resolved'),
                func.sum(case((Report.status == ReportStatus.PENDING, 1), else_=0)).label('pending')
            )
            .filter(Report.created_at >= cutoff_date)
            .group_by('date')
            .order_by('date')
            .all()
        )
        
        data = []
        for r in results:
            data.append({
                "date": r.date.isoformat(),
                "total": r.total,
                "resolved": r.resolved or 0,
                "pending": r.pending or 0,
                "resolution_rate": round((r.resolved / r.total * 100) if r.total > 0 else 0, 2)
            })
        
        return data
    
    # ========================================================================
    # DEPARTMENT PERFORMANCE
    # ========================================================================
    
    def get_department_stats(self) -> List[Dict[str, Any]]:
        """
        Get performance statistics by department
        
        Returns list of departments with metrics:
        - total_assigned
        - completed
        - in_progress
        - overdue
        - avg_response_time
        - avg_resolution_time
        - completion_rate
        """
        departments = self.db.query(Department).all()
        
        stats = []
        for dept in departments:
            assignments = (
                self.db.query(ReportAssignment)
                .filter(ReportAssignment.department_id == dept.id)
                .all()
            )
            
            total_assigned = len(assignments)
            completed = len([a for a in assignments if a.status == 'COMPLETED'])
            in_progress = len([a for a in assignments if a.status == 'WORKING'])
            overdue = len([a for a in assignments if a.is_overdue])
            
            # Calculate avg times
            if assignments:
                response_times = [
                    (a.accepted_at - a.assigned_at).total_seconds() / 3600
                    for a in assignments if a.accepted_at and a.assigned_at
                ]
                avg_response = sum(response_times) / len(response_times) if response_times else 0
                
                resolution_times = [
                    (a.completed_at - a.assigned_at).total_seconds() / 3600
                    for a in assignments if a.completed_at and a.assigned_at
                ]
                avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            else:
                avg_response = 0
                avg_resolution = 0
            
            completion_rate = (completed / total_assigned * 100) if total_assigned > 0 else 0
            
            stats.append({
                "department_id": dept.id,
                "department_name": dept.name,
                "total_assigned": total_assigned,
                "completed": completed,
                "in_progress": in_progress,
                "overdue": overdue,
                "avg_response_time_hours": round(avg_response, 2),
                "avg_resolution_time_hours": round(avg_resolution, 2),
                "completion_rate": round(completion_rate, 2)
            })
        
        return sorted(stats, key=lambda x: x['completion_rate'], reverse=True)
    
    # ========================================================================
    # TOP REPORTERS
    # ========================================================================
    
    def get_top_reporters(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get users with most reports"""
        results = (
            self.db.query(
                User.id,
                User.username,
                User.full_name,
                User.avatar_url,
                func.count(Report.id).label('report_count'),
                User.reputation_score
            )
            .join(Report, Report.user_id == User.id)
            .group_by(User.id)
            .order_by(func.count(Report.id).desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "user_id": r.id,
                "username": r.username,
                "full_name": r.full_name,
                "avatar_url": r.avatar_url,
                "report_count": r.report_count,
                "reputation_score": float(r.reputation_score) if r.reputation_score else 0
            }
            for r in results
        ]


# Singleton
def get_statistics_service(db: Session) -> StatisticsService:
    """Get statistics service instance"""
    return StatisticsService(db)
