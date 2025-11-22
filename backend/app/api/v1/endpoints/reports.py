# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Report endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter()


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    # TODO: Add current_user dependency
):
    """Tạo báo cáo mới"""
    # Placeholder - cần implement logic tạo report với PostGIS
    return {"message": "Endpoint chưa hoàn thiện"}


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """Lấy thống kê báo cáo"""
    from app.models.report import ReportStatus
    
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == ReportStatus.CHO_XAC_NHAN).count()
    active_incidents = db.query(Report).filter(
        Report.status.in_([ReportStatus.CHO_XAC_NHAN, ReportStatus.DA_XAC_NHAN])
    ).count()
    
    return {
        "total": total,
        "pending": pending,
        "active_incidents": active_incidents,
        "active_users": 0,  # TODO: Implement user statistics
    }


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy danh sách báo cáo"""
    query = db.query(Report)
    if status:
        query = query.filter(Report.status == status)
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Lấy chi tiết báo cáo"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy báo cáo"
        )
    return report


@router.get("/nearby", response_model=List[ReportResponse])
def get_nearby_reports(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(5000, ge=100, le=50000),  # meters
    db: Session = Depends(get_db)
):
    """Lấy báo cáo gần vị trí"""
    # Placeholder - cần implement spatial query với PostGIS
    return []
