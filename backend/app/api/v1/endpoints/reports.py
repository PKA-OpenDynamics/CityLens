# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

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
    # TODO: Fix Report model to match actual database schema
    return {
        "total": 0,
        "pending": 0,
        "active_incidents": 0,
        "active_users": 0,
        "today": 0
    }


@router.get("/")
def get_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy danh sách báo cáo"""
    # TODO: Fix Report model to match actual database schema
    # Current schema uses UUID, reporter_id, category_id
    # Model expects Integer, user_id, category string
    return {"reports": [], "total": 0, "skip": skip, "limit": limit}


@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Lấy chi tiết báo cáo"""
    # TODO: Fix Report model to match actual database schema
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Report endpoint temporarily unavailable - schema mismatch"
    )


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
