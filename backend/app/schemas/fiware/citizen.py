# Copyright 2025 CityLens Team
# Licensed under the Apache License, Version 2.0

"""
CityLens Citizen Report Model
Custom model for citizen-generated reports, compatible with NGSI-LD
"""

from pydantic import Field, ConfigDict
from typing import Optional, List

from app.schemas.ngsi_ld.base import (
    NGSILDEntity,
    NGSILDProperty,
    NGSILDGeoProperty,
    NGSILDRelationship,
)


class CitizenReport(NGSILDEntity):
    """
    CityLens Model: CitizenReport
    
    Represents a report submitted by a citizen through the mobile/web app.
    This model bridges traditional report data with NGSI-LD/SOSA standards.
    
    Key Innovation: Citizens as Sensors - each report is an observation
    made by a human sensor.
    """
    
    type: str = Field(default="CitizenReport", const=True)
    
    # Required
    dateReported: NGSILDProperty = Field(
        ...,
        description="Date and time when report was submitted"
    )
    location: NGSILDGeoProperty = Field(
        ...,
        description="Location of the reported issue"
    )
    category: NGSILDProperty = Field(
        ...,
        description="Report category: infrastructure, environment, traffic, security, service, other"
    )
    
    # Report content
    title: Optional[NGSILDProperty] = Field(
        None,
        description="Brief title of the report"
    )
    description: NGSILDProperty = Field(
        ...,
        description="Detailed description of the issue"
    )
    
    # Subcategory
    subcategory: Optional[NGSILDProperty] = Field(
        None,
        description="More specific category"
    )
    
    # Media evidence
    images: Optional[NGSILDProperty] = Field(
        None,
        description="Array of image URLs"
    )
    videos: Optional[NGSILDProperty] = Field(
        None,
        description="Array of video URLs"
    )
    
    # Status tracking
    status: NGSILDProperty = Field(
        default=NGSILDProperty(value="pending"),
        description="Status: pending, verified, in_progress, resolved, rejected"
    )
    priority: Optional[NGSILDProperty] = Field(
        None,
        description="Priority level: low, normal, high, urgent"
    )
    
    # Severity (for risk assessment)
    severity: Optional[NGSILDProperty] = Field(
        None,
        description="Severity level: minor, moderate, major, critical"
    )
    
    # Address
    address: Optional[NGSILDProperty] = Field(
        None,
        description="Human-readable address"
    )
    
    # Relationships
    reportedBy: NGSILDRelationship = Field(
        ...,
        description="Reference to the citizen who reported (User entity)"
    )
    refDistrict: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to the district"
    )
    refStreet: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to the street"
    )
    refFacility: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to nearby facility (if relevant)"
    )
    
    # Verification
    verifiedBy: Optional[NGSILDRelationship] = Field(
        None,
        description="Reference to admin/moderator who verified"
    )
    verifiedAt: Optional[NGSILDProperty] = Field(
        None,
        description="Verification timestamp"
    )
    
    # Resolution
    resolvedAt: Optional[NGSILDProperty] = Field(
        None,
        description="Resolution timestamp"
    )
    resolution: Optional[NGSILDProperty] = Field(
        None,
        description="Resolution notes"
    )
    
    # Engagement metrics
    upvotes: Optional[NGSILDProperty] = Field(
        None,
        description="Number of upvotes from other citizens"
    )
    downvotes: Optional[NGSILDProperty] = Field(
        None,
        description="Number of downvotes"
    )
    views: Optional[NGSILDProperty] = Field(
        None,
        description="Number of views"
    )
    commentsCount: Optional[NGSILDProperty] = Field(
        None,
        description="Number of comments"
    )
    
    # Device info (for data quality)
    deviceInfo: Optional[NGSILDProperty] = Field(
        None,
        description="Information about the device used to submit report"
    )
    appVersion: Optional[NGSILDProperty] = Field(
        None,
        description="App version used"
    )
    
    # Confidence score (for AI validation)
    confidenceScore: Optional[NGSILDProperty] = Field(
        None,
        description="AI-calculated confidence score (0-1)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "urn:ngsi-ld:CitizenReport:HCM-2025-11-25-001",
                "type": "CitizenReport",
                "dateReported": {
                    "type": "Property",
                    "value": "2025-11-25T08:30:00Z"
                },
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [106.660172, 10.762622]
                    }
                },
                "category": {
                    "type": "Property",
                    "value": "infrastructure"
                },
                "subcategory": {
                    "type": "Property",
                    "value": "road_damage"
                },
                "title": {
                    "type": "Property",
                    "value": "Large pothole on Nguyen Hue Street"
                },
                "description": {
                    "type": "Property",
                    "value": "There is a large pothole (approximately 1 meter diameter) near the intersection causing traffic issues",
                    "language": "en"
                },
                "images": {
                    "type": "Property",
                    "value": [
                        "https://citylens.io/uploads/images/abc123.jpg",
                        "https://citylens.io/uploads/images/def456.jpg"
                    ]
                },
                "status": {
                    "type": "Property",
                    "value": "pending"
                },
                "priority": {
                    "type": "Property",
                    "value": "high"
                },
                "severity": {
                    "type": "Property",
                    "value": "major"
                },
                "address": {
                    "type": "Property",
                    "value": "Nguyen Hue Street, District 1, Ho Chi Minh City"
                },
                "reportedBy": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:User:456"
                },
                "refDistrict": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:District:1"
                },
                "refStreet": {
                    "type": "Relationship",
                    "object": "urn:ngsi-ld:Street:789"
                },
                "upvotes": {
                    "type": "Property",
                    "value": 15
                },
                "views": {
                    "type": "Property",
                    "value": 234
                },
                "confidenceScore": {
                    "type": "Property",
                    "value": 0.92,
                    "description": "High confidence based on image analysis and user reputation"
                },
                "@context": [
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                    "http://citylens.io/context/citylens-context.jsonld"
                ]
            }
        }
    )

