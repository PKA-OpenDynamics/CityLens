# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Media models - Files đính kèm (images, videos)
"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import enum
import uuid
from app.db.postgres import Base


class MediaType(str, enum.Enum):
    """Loại media"""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"


class MediaFile(Base):
    """File media chung"""
    __tablename__ = "media_files"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(Enum(MediaType), nullable=False, index=True)
    mime_type = Column(String(100), nullable=False)
    
    # Storage
    storage_path = Column(String(500), nullable=False, comment="Path in storage system")
    storage_type = Column(String(50), default="local", comment="local, s3, cloudinary")
    
    # File properties
    file_size = Column(BigInteger, nullable=False, comment="Size in bytes")
    width = Column(Integer, comment="Image/video width")
    height = Column(Integer, comment="Image/video height")
    duration = Column(Integer, comment="Video duration in seconds")
    
    # Uploader
    uploaded_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<MediaFile {self.filename} ({self.file_type})>"


class ReportMedia(Base):
    """Link giữa Report và MediaFile"""
    __tablename__ = "report_media"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(PGUUID(as_uuid=True), ForeignKey("reports.id"), nullable=False, index=True)
    media_id = Column(PGUUID(as_uuid=True), ForeignKey("media_files.id"), nullable=False, index=True)
    
    # Order in report
    display_order = Column(Integer, default=0)
    
    # Is this the primary/cover image?
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ReportMedia report={self.report_id} media={self.media_id}>"
