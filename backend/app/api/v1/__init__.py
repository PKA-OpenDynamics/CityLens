# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import reports, notifications, engagement, assignments, geographic, statistics, media, realtime

api_router = APIRouter()

# Include all endpoint routers  
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["User Engagement"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(geographic.router, prefix="/geographic", tags=["Geographic"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(realtime.router, prefix="/realtime", tags=["Real-time"])
