# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Import all models here for Alembic to detect them
"""

from app.db.postgres import Base

# Layer 1: Geographic data (OSM)
from app.models.geographic import (
    AdministrativeBoundary,
    Street,
    Building,
    POI
)

# Layer 2: Urban infrastructure
from app.models.facility import (
    PublicFacility,
    TransportFacility
)

from app.models.environment import EnvironmentalData

# Layer 3: Citizen data
from app.models.user import User, UserRole
from app.models.report import (
    Report,
    ReportCategory,
    ReportStatus,
    ReportPriority
)

# Engagement & Management
from app.models.notification import Notification, NotificationType
from app.models.assignment import ReportAssignment, Department, AssignmentStatus, DepartmentMember, AssignmentHistory
from app.models.media import MediaFile, ReportMedia, MediaType
from app.models.incident import Incident, IncidentType, IncidentSeverity

# NGSI-LD entities
from app.models.db_models import EntityDB

__all__ = [
    "Base",
    # Geographic
    "AdministrativeBoundary",
    "Street", 
    "Building",
    "POI",
    # Facilities
    "PublicFacility",
    "TransportFacility",
    "EnvironmentalData",
    # Users & Reports
    "User",
    "UserRole",
    "Report",
    "ReportCategory",
    "ReportStatus",
    "ReportPriority",
    # Engagement
    "Notification",
    "NotificationType",
    "ReportAssignment",
    "Department",
    "AssignmentStatus",
    "MediaFile",
    "ReportMedia",
    "MediaType",
    # NGSI-LD
    "EntityDB",
]
