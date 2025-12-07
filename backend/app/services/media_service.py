# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Media Service - File upload, processing, and management
Handles image resize, thumbnail generation, validation
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from datetime import datetime
from PIL import Image
import io

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.media import MediaFile, ReportMedia
from app.core.config import settings


class MediaService:
    """Service for handling media uploads and processing"""
    
    # Configuration
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB
    
    THUMBNAIL_SIZE = (300, 300)
    MEDIUM_SIZE = (800, 800)
    LARGE_SIZE = (1920, 1920)
    
    UPLOAD_DIR = Path("uploads")
    
    def __init__(self, db: Session):
        self.db = db
        self._ensure_upload_dirs()
    
    def _ensure_upload_dirs(self):
        """Create upload directories if they don't exist"""
        dirs = [
            self.UPLOAD_DIR,
            self.UPLOAD_DIR / "reports",
            self.UPLOAD_DIR / "reports" / "originals",
            self.UPLOAD_DIR / "reports" / "thumbnails",
            self.UPLOAD_DIR / "reports" / "medium",
            self.UPLOAD_DIR / "avatars",
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile, file_type: str = "image") -> None:
        """
        Validate file size and type
        
        Args:
            file: Uploaded file
            file_type: 'image' or 'video'
            
        Raises:
            HTTPException: If validation fails
        """
        # Check content type
        if file_type == "image":
            if file.content_type not in self.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type. Allowed: {', '.join(self.ALLOWED_IMAGE_TYPES)}"
                )
        elif file_type == "video":
            if file.content_type not in self.ALLOWED_VIDEO_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid video type. Allowed: {', '.join(self.ALLOWED_VIDEO_TYPES)}"
                )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        max_size = self.MAX_IMAGE_SIZE if file_type == "image" else self.MAX_FILE_SIZE
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {max_size / (1024*1024):.1f}MB"
            )
    
    async def process_image(
        self, 
        file: UploadFile, 
        user_id: int,
        category: str = "reports"
    ) -> MediaFile:
        """
        Process and save image with multiple sizes
        
        Args:
            file: Uploaded image file
            user_id: User who uploaded
            category: Category for organization (reports, avatars)
            
        Returns:
            MediaFile object
        """
        # Validate
        await self.validate_file(file, "image")
        
        # Generate unique filename
        file_ext = Path(file.filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        base_filename = f"{unique_id}{file_ext}"
        
        # Date-based path
        now = datetime.now()
        date_path = f"{now.year}/{now.month:02d}"
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Get original dimensions
        width, height = image.size
        
        # Save original
        original_dir = self.UPLOAD_DIR / category / "originals" / date_path
        original_dir.mkdir(parents=True, exist_ok=True)
        original_path = original_dir / base_filename
        image.save(original_path, quality=95, optimize=True)
        
        # Generate thumbnail
        thumbnail_dir = self.UPLOAD_DIR / category / "thumbnails" / date_path
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = thumbnail_dir / base_filename
        thumbnail = image.copy()
        thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        thumbnail.save(thumbnail_path, quality=85, optimize=True)
        
        # Generate medium size
        medium_dir = self.UPLOAD_DIR / category / "medium" / date_path
        medium_dir.mkdir(parents=True, exist_ok=True)
        medium_path = medium_dir / base_filename
        medium = image.copy()
        medium.thumbnail(self.MEDIUM_SIZE, Image.Resampling.LANCZOS)
        medium.save(medium_path, quality=90, optimize=True)
        
        # Create database record
        media = MediaFile(
            user_id=user_id,
            file_type="image",
            original_filename=file.filename,
            file_path=str(original_path.relative_to(self.UPLOAD_DIR)),
            file_url=f"/uploads/{original_path.relative_to(self.UPLOAD_DIR)}",
            thumbnail_url=f"/uploads/{thumbnail_path.relative_to(self.UPLOAD_DIR)}",
            file_size=len(contents),
            mime_type=file.content_type,
            width=width,
            height=height,
            metadata={
                "medium_url": f"/uploads/{medium_path.relative_to(self.UPLOAD_DIR)}",
                "original_filename": file.filename,
            }
        )
        
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        
        return media
    
    async def attach_media_to_report(
        self,
        report_id: int,
        media_id: int,
        display_order: int = 0,
        caption: Optional[str] = None
    ) -> ReportMedia:
        """
        Attach media to a report
        
        Args:
            report_id: Report ID
            media_id: Media file ID
            display_order: Order in gallery
            caption: Optional caption
            
        Returns:
            ReportMedia relationship
        """
        # Check if already attached
        existing = self.db.query(ReportMedia).filter(
            ReportMedia.report_id == report_id,
            ReportMedia.media_id == media_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Media already attached to this report")
        
        report_media = ReportMedia(
            report_id=report_id,
            media_id=media_id,
            display_order=display_order,
            caption=caption
        )
        
        self.db.add(report_media)
        self.db.commit()
        self.db.refresh(report_media)
        
        return report_media
    
    def get_media_by_id(self, media_id: int) -> Optional[MediaFile]:
        """Get media file by ID"""
        return self.db.query(MediaFile).filter(MediaFile.id == media_id).first()
    
    def get_report_media(self, report_id: int) -> list[MediaFile]:
        """Get all media files for a report, ordered"""
        results = (
            self.db.query(MediaFile)
            .join(ReportMedia)
            .filter(ReportMedia.report_id == report_id)
            .order_by(ReportMedia.display_order)
            .all()
        )
        return results
    
    async def delete_media(self, media_id: int, user_id: int) -> bool:
        """
        Delete media file
        
        Args:
            media_id: Media file ID
            user_id: User requesting deletion (must be owner or admin)
            
        Returns:
            True if deleted
        """
        media = self.get_media_by_id(media_id)
        if not media:
            raise HTTPException(status_code=404, detail="Media not found")
        
        if media.user_id != user_id:
            # TODO: Check if user is admin
            raise HTTPException(status_code=403, detail="Not authorized to delete this media")
        
        # Delete physical files
        try:
            file_path = self.UPLOAD_DIR / media.file_path
            if file_path.exists():
                file_path.unlink()
            
            # Delete thumbnail
            if media.thumbnail_url:
                thumb_path = self.UPLOAD_DIR / media.thumbnail_url.replace("/uploads/", "")
                if thumb_path.exists():
                    thumb_path.unlink()
            
            # Delete medium
            if media.metadata and "medium_url" in media.metadata:
                medium_path = self.UPLOAD_DIR / media.metadata["medium_url"].replace("/uploads/", "")
                if medium_path.exists():
                    medium_path.unlink()
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        # Delete from database (cascade will handle report_media)
        self.db.delete(media)
        self.db.commit()
        
        return True


# Singleton instance
_media_service = None

def get_media_service(db: Session) -> MediaService:
    """Get or create media service instance"""
    return MediaService(db)
