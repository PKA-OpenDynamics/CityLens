# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Admin endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.schemas.report import ReportVerify

router = APIRouter()


@router.get("/reports/stats")
def get_report_statistics(
    db: Session = Depends(get_db),
    # TODO: Add admin authentication
):
    """Thống kê báo cáo (chỉ admin)"""
    # Placeholder - cần implement admin authorization
    return {"message": "Endpoint dành cho admin"}


@router.put("/reports/{report_id}/verify")
def verify_report(
    report_id: int,
    verify_data: ReportVerify,
    db: Session = Depends(get_db),
    # TODO: Add admin authentication
):
    """Xác thực báo cáo (chỉ admin)"""
    # Placeholder - cần implement admin authorization
    return {"message": "Endpoint dành cho admin"}
