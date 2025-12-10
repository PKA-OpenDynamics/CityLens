# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App Report Service
Handles report CRUD operations for mobile app
Uses MongoDB Atlas (cloud)
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status

from app.schemas.app_report import AppReport, AppReportCreate


class AppReportService:
    """Report management service for mobile app"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reports
        # Initialize indexes for performance (runs once per connection)
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure database indexes exist for optimal query performance"""
        try:
            # Index for status queries
            self.collection.create_index([("status", 1), ("createdAt", -1)])
            # Index for userId queries
            self.collection.create_index([("userId", 1), ("createdAt", -1)])
            # Compound index for common queries
            self.collection.create_index([("status", 1), ("userId", 1), ("createdAt", -1)])
            # Index for ward-based queries
            self.collection.create_index([("ward", 1), ("createdAt", -1)])
            # Index for reportType queries
            self.collection.create_index([("reportType", 1), ("createdAt", -1)])
        except Exception as e:
            # Indexes might already exist
            pass
    
    async def create_report(self, report_data: AppReportCreate) -> AppReport:
        """Create a new report"""
        # Create report document (matching web-app/server structure)
        report_doc = {
            "_id": ObjectId(),
            "reportType": report_data.reportType,
            "ward": report_data.ward,
            "addressDetail": report_data.addressDetail or "",
            "location": report_data.location.dict() if report_data.location else None,
            "title": report_data.title or "",
            "content": report_data.content,
            "media": [media.dict() for media in report_data.media],
            "userId": report_data.userId,
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        
        result = await self.collection.insert_one(report_doc)
        
        report_doc["_id"] = str(result.inserted_id)
        return AppReport(**report_doc)
    
    async def get_reports(
        self,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 20,
        skip: int = 0,
        include_media: bool = True
    ) -> List[dict]:
        """Get reports list with filters (optimized with smart projection)"""
        query = {}
        
        if status:
            query["status"] = status
        
        if user_id:
            query["userId"] = user_id
        
        # Projection: only fetch needed fields to reduce data transfer
        projection = {
            "_id": 1,
            "reportType": 1,
            "ward": 1,
            "addressDetail": 1,
            "location": 1,
            "title": 1,
            "content": 1,
            "status": 1,
            "createdAt": 1,
            "updatedAt": 1,
            "userId": 1,
            "adminNote": 1
        }
        
        # Include media based on parameter
        if include_media:
            # For media, only fetch first image thumbnail for list view
            projection["media"] = {"$slice": 3}  # Limit to first 3 media items
        
        # Use hint to force index usage for better performance
        cursor = self.collection.find(
            query,
            projection
        ).sort("createdAt", -1).limit(limit).skip(skip)
        
        reports = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for report in reports:
            report["_id"] = str(report["_id"])
            if not include_media:
                report["media"] = []  # Empty array if media not fetched
        
        return reports
    
    async def get_reports_count(
        self,
        status: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> int:
        """Get total count of reports matching filters (optimized)"""
        query = {}
        
        if status:
            query["status"] = status
        
        if user_id:
            query["userId"] = user_id
        
        # Use count_documents for accurate count
        count = await self.collection.count_documents(query)
        return count
    
    async def get_report_by_id(self, report_id: str) -> Optional[dict]:
        """Get a specific report by ID"""
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID không hợp lệ"
            )
        
        report = await self.collection.find_one({"_id": ObjectId(report_id)})
        
        if not report:
            return None
        
        report["_id"] = str(report["_id"])
        return report
    
    async def get_reports_summary(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[dict]:
        """Get reports summary (optimized for map view - no media)"""
        query = {}
        
        if status:
            query["status"] = status
        
        # Minimal projection for map markers
        projection = {
            "_id": 1,
            "reportType": 1,
            "ward": 1,
            "location": 1,
            "title": 1,
            "status": 1,
            "createdAt": 1
        }
        
        cursor = self.collection.find(
            query,
            projection
        ).sort("createdAt", -1).limit(limit).skip(skip)
        
        reports = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for report in reports:
            report["_id"] = str(report["_id"])
        
        return reports
    
    async def update_report_status(
        self,
        report_id: str,
        new_status: str,
        admin_note: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        report_type: Optional[str] = None,
        ward: Optional[str] = None,
        address_detail: Optional[str] = None
    ) -> dict:
        """Update report (admin only)"""
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID không hợp lệ"
            )
        
        update_data = {
            "updatedAt": datetime.utcnow(),
        }
        
        # Only update fields that are provided
        if new_status:
            update_data["status"] = new_status
        if admin_note is not None:
            update_data["adminNote"] = admin_note
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if report_type is not None:
            update_data["reportType"] = report_type
        if ward is not None:
            update_data["ward"] = ward
        if address_detail is not None:
            update_data["addressDetail"] = address_detail
        
        result = await self.collection.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy report"
            )
        
        return await self.get_report_by_id(report_id)
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete a report"""
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID không hợp lệ"
            )
        
        result = await self.collection.delete_one({"_id": ObjectId(report_id)})
        
        return result.deleted_count > 0
    
    async def count_reports(self, status: Optional[str] = None, user_id: Optional[str] = None) -> int:
        """Count reports with optional filters"""
        query = {}
        
        if status:
            query["status"] = status
        
        if user_id:
            query["userId"] = user_id
        
        return await self.collection.count_documents(query)
