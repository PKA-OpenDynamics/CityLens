# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Database base configuration
Base class for all SQLAlchemy models
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Note: Do NOT import models here to avoid circular imports
# Models should import Base from here, not the other way around
# For Alembic, models are imported in alembic/env.py
