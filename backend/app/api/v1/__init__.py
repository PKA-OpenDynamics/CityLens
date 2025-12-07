# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, reports, ngsi_ld, notifications, engagement, assignments, admin, geographic

api_router = APIRouter()

# Include all endpoint routers  
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["User Engagement"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(geographic.router, tags=["Geographic Data"])

# NGSI-LD endpoints (mounted at root level, not under /api/v1)
# These will be available at /ngsi-ld/v1/...
# But we export the router here for registration in main.py
ngsi_ld_router = ngsi_ld.router
