# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API router tổng hợp
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, reports, incidents, admin,
    media, statistics, ngsi_ld, engagement, 
    assignments, notifications
)

api_router = APIRouter()

# Core APIs
api_router.include_router(auth.router, prefix="/auth", tags=["Xác thực"])
api_router.include_router(users.router, prefix="/users", tags=["Người dùng"])
api_router.include_router(reports.router, prefix="/reports", tags=["Báo cáo"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Sự kiện"])
api_router.include_router(admin.router, prefix="/admin", tags=["Quản trị"])

# New APIs
api_router.include_router(media.router, tags=["Media"])
api_router.include_router(statistics.router, tags=["Statistics"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["Engagement"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# NGSI-LD
api_router.include_router(ngsi_ld.router, tags=["NGSI-LD"])
