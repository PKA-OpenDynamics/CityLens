# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API router tổng hợp
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, reports, incidents, admin, weather

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Xác thực"])
api_router.include_router(users.router, prefix="/users", tags=["Người dùng"])
api_router.include_router(reports.router, prefix="/reports", tags=["Báo cáo"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Sự kiện"])
api_router.include_router(admin.router, prefix="/admin", tags=["Quản trị"])
api_router.include_router(weather.router, prefix="/weather", tags=["Thời tiết & Không khí"])
