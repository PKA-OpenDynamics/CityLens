# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Incident endpoints (real-time events)
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.postgres import get_db
from app.models.incident import Incident

router = APIRouter()


@router.get("/")
def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Lấy danh sách sự kiện đang diễn ra"""
    incidents = db.query(Incident).filter(
        Incident.is_active == 1
    ).offset(skip).limit(limit).all()
    return incidents


@router.get("/heatmap")
def get_heatmap_data(
    incident_type: str = Query(None),
    db: Session = Depends(get_db)
):
    """Lấy dữ liệu heatmap"""
    # Placeholder - cần implement heatmap data aggregation
    return {
        "type": "FeatureCollection",
        "features": []
    }
