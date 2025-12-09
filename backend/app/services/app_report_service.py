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
        skip: int = 0
    ) -> List[dict]:
        """Get reports list with filters"""
        query = {}
        
        if status:
            query["status"] = status
        
        if user_id:
            query["userId"] = user_id
        
        cursor = self.collection.find(query).sort("createdAt", -1).limit(limit).skip(skip)
        
        reports = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for report in reports:
            report["_id"] = str(report["_id"])
        
        return reports
    
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
    
    async def update_report_status(
        self,
        report_id: str,
        new_status: str,
        admin_note: Optional[str] = None
    ) -> dict:
        """Update report status (admin only)"""
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID không hợp lệ"
            )
        
        update_data = {
            "status": new_status,
            "updatedAt": datetime.utcnow(),
        }
        
        if admin_note:
            update_data["adminNote"] = admin_note
        
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
