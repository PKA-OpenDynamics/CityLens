# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Database base configuration
Import all models here for Alembic autogenerate
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so Alembic can detect them
from app.models.user import User  # noqa
from app.models.report import Report, ReportCategory, ReportComment, ReportVote, ReportFollower, ReportActivity  # noqa
from app.models.geographic import AdministrativeBoundary, Street, Building  # noqa
from app.models.facility import PublicFacility, TransportFacility  # noqa
from app.models.environment import EnvironmentalData  # noqa
