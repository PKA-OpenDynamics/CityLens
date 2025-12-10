# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
FiWARE Smart Data Model: CivicIssueTracking
https://github.com/smart-data-models/dataModel.IssueTracking/tree/master/CivicIssueTracking

NGSI-LD compliant civic issue tracking for citizen reports.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from enum import Enum


class IssueStatus(str, Enum):
    """Issue status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "inProgress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class IssuePriority(str, Enum):
    """Issue priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CivicIssueTrackingBase(BaseModel):
    """Base schema for CivicIssueTracking"""
    # Location
    location: Dict[str, Any] = Field(..., description="GeoJSON Point")
    address: Optional[Dict[str, str]] = Field(None, description="Civic address")
    
    # Issue details
    title: str = Field(..., description="Issue title", min_length=1, max_length=200)
    description: str = Field(..., description="Detailed description", min_length=1)
    
    # Category
    category: str = Field(..., description="Category: streetLighting, roadDamage, waste, etc.")
    subCategory: Optional[str] = Field(None, description="Subcategory")
    
    # Status and priority
    status: IssueStatus = Field(default=IssueStatus.OPEN, description="Current status")
    priority: Optional[IssuePriority] = Field(None, description="Priority level")
    
    # Reporter
    reportedBy: Optional[str] = Field(None, description="Reporter user ID or name")
    reporterEmail: Optional[str] = Field(None, description="Reporter email")
    reporterPhone: Optional[str] = Field(None, description="Reporter phone")
    
    # Assignment
    assignedTo: Optional[str] = Field(None, description="Assigned department or person")
    
    # Media
    imageUrls: Optional[List[str]] = Field(None, description="List of image URLs")
    videoUrls: Optional[List[str]] = Field(None, description="List of video URLs")
    
    # Engagement
    upvotes: Optional[int] = Field(0, ge=0, description="Number of upvotes")
    downvotes: Optional[int] = Field(0, ge=0, description="Number of downvotes")
    comments: Optional[int] = Field(0, ge=0, description="Number of comments")
    
    # Timestamps
    dateCreated: datetime = Field(..., description="Creation timestamp")
    dateModified: Optional[datetime] = Field(None, description="Last modification timestamp")
    dateResolved: Optional[datetime] = Field(None, description="Resolution timestamp")


class CivicIssueTrackingCreate(CivicIssueTrackingBase):
    """Schema for creating CivicIssueTracking"""
    pass


class CivicIssueTracking(CivicIssueTrackingBase):
    """Full NGSI-LD CivicIssueTracking entity"""
    id: str = Field(..., description="URN: urn:ngsi-ld:CivicIssueTracking:{id}")
    type: Literal["CivicIssueTracking"] = "CivicIssueTracking"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "urn:ngsi-ld:CivicIssueTracking:Hanoi-20241209-001",
                "type": "CivicIssueTracking",
                "location": {
                    "type": "Point",
                    "coordinates": [105.8342, 21.0278]
                },
                "address": {
                    "streetAddress": "Nguyễn Trãi Street",
                    "addressLocality": "Thanh Xuân District",
                    "addressRegion": "Hanoi",
                    "addressCountry": "VN"
                },
                "title": "Broken street light",
                "description": "Street light on Nguyen Trai is not working for 3 days",
                "category": "streetLighting",
                "status": "open",
                "priority": "medium",
                "reportedBy": "Nguyen Van A",
                "reporterEmail": "nguyenvana@example.com",
                "imageUrls": ["https://example.com/images/issue-001.jpg"],
                "upvotes": 15,
                "comments": 3,
                "dateCreated": "2024-12-09T08:30:00Z"
            }
        }


def to_ngsi_ld_entity(data: CivicIssueTrackingCreate, entity_id: str) -> Dict[str, Any]:
    """
    Convert CivicIssueTracking to full NGSI-LD entity format
    """
    entity = {
        "id": entity_id,
        "type": "CivicIssueTracking",
        "@context": [
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
            "https://raw.githubusercontent.com/smart-data-models/dataModel.IssueTracking/master/context.jsonld"
        ]
    }
    
    # Location (GeoProperty)
    entity["location"] = {
        "type": "GeoProperty",
        "value": data.location
    }
    
    # Address
    if data.address:
        entity["address"] = {
            "type": "Property",
            "value": data.address
        }
    
    # Issue details
    entity["title"] = {
        "type": "Property",
        "value": data.title
    }
    
    entity["description"] = {
        "type": "Property",
        "value": data.description
    }
    
    # Category
    entity["category"] = {
        "type": "Property",
        "value": data.category
    }
    
    if data.subCategory:
        entity["subCategory"] = {
            "type": "Property",
            "value": data.subCategory
        }
    
    # Status and priority
    entity["status"] = {
        "type": "Property",
        "value": data.status.value,
        "observedAt": (data.dateModified or data.dateCreated).isoformat() + "Z"
    }
    
    if data.priority:
        entity["priority"] = {
            "type": "Property",
            "value": data.priority.value
        }
    
    # Reporter
    if data.reportedBy:
        entity["reportedBy"] = {
            "type": "Property",
            "value": data.reportedBy
        }
    
    if data.reporterEmail:
        entity["reporterEmail"] = {
            "type": "Property",
            "value": data.reporterEmail
        }
    
    if data.reporterPhone:
        entity["reporterPhone"] = {
            "type": "Property",
            "value": data.reporterPhone
        }
    
    # Assignment
    if data.assignedTo:
        entity["assignedTo"] = {
            "type": "Property",
            "value": data.assignedTo
        }
    
    # Media
    if data.imageUrls:
        entity["imageUrls"] = {
            "type": "Property",
            "value": data.imageUrls
        }
    
    if data.videoUrls:
        entity["videoUrls"] = {
            "type": "Property",
            "value": data.videoUrls
        }
    
    # Engagement metrics
    if data.upvotes is not None:
        entity["upvotes"] = {
            "type": "Property",
            "value": data.upvotes
        }
    
    if data.downvotes is not None:
        entity["downvotes"] = {
            "type": "Property",
            "value": data.downvotes
        }
    
    if data.comments is not None:
        entity["comments"] = {
            "type": "Property",
            "value": data.comments
        }
    
    # Timestamps
    entity["dateCreated"] = {
        "type": "Property",
        "value": {
            "@type": "DateTime",
            "@value": data.dateCreated.isoformat() + "Z"
        }
    }
    
    if data.dateModified:
        entity["dateModified"] = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": data.dateModified.isoformat() + "Z"
            }
        }
    
    if data.dateResolved:
        entity["dateResolved"] = {
            "type": "Property",
            "value": {
                "@type": "DateTime",
                "@value": data.dateResolved.isoformat() + "Z"
            }
        }
    
    return entity
