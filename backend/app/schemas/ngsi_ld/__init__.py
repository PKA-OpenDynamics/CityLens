# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
NGSI-LD Schemas
Standard: ETSI GS CIM 009 V1.6.1
https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.06.01_60/gs_CIM009v010601p.pdf
"""

from .base import (
    NGSILDProperty,
    NGSILDGeoProperty,
    NGSILDRelationship,
    NGSILDEntity,
    NGSILDContext,
)
from .query import (
    NGSILDQuery,
    NGSILDGeoQuery,
)

__all__ = [
    "NGSILDProperty",
    "NGSILDGeoProperty",
    "NGSILDRelationship",
    "NGSILDEntity",
    "NGSILDContext",
    "NGSILDQuery",
    "NGSILDGeoQuery",
]

