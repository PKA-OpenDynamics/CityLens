# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
API v1 Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, reports, categories, ngsi_ld

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# NGSI-LD endpoints (mounted at root level, not under /api/v1)
# These will be available at /ngsi-ld/v1/...
# But we export the router here for registration in main.py
ngsi_ld_router = ngsi_ld.router
