# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Mobile App Comment Service
Handles comment CRUD operations for mobile app reports
Uses MongoDB Atlas (cloud)
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status


class AppCommentService:
    """Comment management service for mobile app"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.comments  # Collection name: comments
    
    async def create_comment(
        self, 
        report_id: str, 
        content: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None
    ) -> dict:
        """Create a new comment on a report"""
        # Validate report exists
        report = await self.db.reports.find_one({"_id": ObjectId(report_id)})
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report không tồn tại"
            )
        
        # Create comment document
        # Use UTC time but ensure it's properly serialized as ISO string with Z suffix
        now = datetime.utcnow()
        comment_doc = {
            "_id": ObjectId(),
            "reportId": report_id,
            "userId": user_id,
            "userName": user_name or "Người dùng",
            "content": content,
            "createdAt": now,
            "updatedAt": now,
        }
        
        result = await self.collection.insert_one(comment_doc)
        
        comment_doc["_id"] = str(result.inserted_id)
        # Convert datetime to ISO format string with timezone for frontend
        if isinstance(comment_doc.get("createdAt"), datetime):
            comment_doc["createdAt"] = comment_doc["createdAt"].isoformat() + "Z"
        if isinstance(comment_doc.get("updatedAt"), datetime):
            comment_doc["updatedAt"] = comment_doc["updatedAt"].isoformat() + "Z"
        
        return comment_doc
    
    async def get_comments(
        self,
        report_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[dict]:
        """Get all comments for a report"""
        if not ObjectId.is_valid(report_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID không hợp lệ"
            )
        
        cursor = self.collection.find({"reportId": report_id}).sort("createdAt", 1).limit(limit).skip(skip)
        
        comments = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string and ensure datetime is ISO format
        for comment in comments:
            comment["_id"] = str(comment["_id"])
            # Ensure createdAt and updatedAt are ISO format strings with timezone
            if isinstance(comment.get("createdAt"), datetime):
                comment["createdAt"] = comment["createdAt"].isoformat() + "Z"
            if isinstance(comment.get("updatedAt"), datetime):
                comment["updatedAt"] = comment["updatedAt"].isoformat() + "Z"
        
        return comments
    
    async def count_comments(self, report_id: str) -> int:
        """Count comments for a report"""
        if not ObjectId.is_valid(report_id):
            return 0
        
        count = await self.collection.count_documents({"reportId": report_id})
        return count
    
    async def delete_comment(self, comment_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a comment (only by owner or admin)"""
        if not ObjectId.is_valid(comment_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment ID không hợp lệ"
            )
        
        query = {"_id": ObjectId(comment_id)}
        
        # If user_id provided, only allow deletion by owner
        if user_id:
            query["userId"] = user_id
        
        result = await self.collection.delete_one(query)
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment không tồn tại hoặc bạn không có quyền xóa"
            )
        
        return True

