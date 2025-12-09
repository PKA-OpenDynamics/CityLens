# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API router tổng hợp
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    reports, media, statistics, engagement, 
    assignments, notifications, geographic, realtime, ngsi_ld
)

api_router = APIRouter()

# NGSI-LD Context Broker (prioritized for compliance)
api_router.include_router(ngsi_ld.router, tags=["NGSI-LD Context Broker"])

# Core APIs
api_router.include_router(reports.router, prefix="/reports", tags=["Báo cáo"])

# Geographic API (Layer 1 - OSM Data)
api_router.include_router(geographic.router, tags=["Geographic"])

# Realtime Data API (Layer 2 - Urban Infrastructure)
api_router.include_router(realtime.router, prefix="/realtime", tags=["Realtime"])

# Additional APIs
api_router.include_router(media.router, tags=["Media"])
api_router.include_router(statistics.router, tags=["Statistics"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["Engagement"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
