# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Media API Endpoints
Handles file uploads, retrieval, and management
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.media import MediaFile
from app.services.media_service import get_media_service, MediaService


router = APIRouter(prefix="/media", tags=["Media"])


# ============================================================================
# SCHEMAS
# ============================================================================

class MediaResponse(BaseModel):
    id: int
    file_type: str
    file_url: str
    thumbnail_url: Optional[str]
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    created_at: str
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    success: bool
    message: str
    media: MediaResponse


class MediaListResponse(BaseModel):
    total: int
    media: List[MediaResponse]


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    category: str = Query("reports", description="Category: reports, avatars"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload image file with automatic processing
    
    - Validates file type and size
    - Generates thumbnail and medium size
    - Returns URLs for all sizes
    - Max size: 5MB for images
    - Allowed: JPEG, PNG, WebP
    """
    media_service = get_media_service(db)
    
    try:
        media = await media_service.process_image(
            file=file,
            user_id=current_user.id,
            category=category
        )
        
        return MediaUploadResponse(
            success=True,
            message="File uploaded successfully",
            media=MediaResponse.from_orm(media)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=dict)
async def upload_multiple_media(
    files: List[UploadFile] = File(...),
    category: str = Query("reports"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload multiple images at once
    
    - Max 5 files per request
    - Same validation as single upload
    - Returns list of uploaded media
    """
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files per upload")
    
    media_service = get_media_service(db)
    uploaded_media = []
    errors = []
    
    for idx, file in enumerate(files):
        try:
            media = await media_service.process_image(
                file=file,
                user_id=current_user.id,
                category=category
            )
            uploaded_media.append(MediaResponse.from_orm(media))
        except Exception as e:
            errors.append({
                "file": file.filename,
                "error": str(e)
            })
    
    return {
        "success": len(uploaded_media) > 0,
        "uploaded": uploaded_media,
        "errors": errors,
        "total_uploaded": len(uploaded_media),
        "total_errors": len(errors)
    }


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    db: Session = Depends(get_db)
):
    """
    Get media file information by ID
    
    Returns metadata including URLs for all sizes
    """
    media_service = get_media_service(db)
    media = media_service.get_media_by_id(media_id)
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return MediaResponse.from_orm(media)


@router.get("/reports/{report_id}/media", response_model=MediaListResponse)
async def get_report_media(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all media files attached to a report
    
    Ordered by display_order
    """
    media_service = get_media_service(db)
    media_list = media_service.get_report_media(report_id)
    
    return MediaListResponse(
        total=len(media_list),
        media=[MediaResponse.from_orm(m) for m in media_list]
    )


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete media file
    
    - Only owner or admin can delete
    - Deletes physical files and database record
    - Cascade deletes report_media relationships
    """
    media_service = get_media_service(db)
    
    await media_service.delete_media(
        media_id=media_id,
        user_id=current_user.id
    )
    
    return None


@router.post("/reports/{report_id}/attach", status_code=201)
async def attach_media_to_report(
    report_id: int,
    media_id: int = Query(...),
    display_order: int = Query(0),
    caption: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Attach existing media to a report
    
    - Creates report_media relationship
    - Allows setting display order and caption
    """
    media_service = get_media_service(db)
    
    # TODO: Verify user owns the report
    
    report_media = await media_service.attach_media_to_report(
        report_id=report_id,
        media_id=media_id,
        display_order=display_order,
        caption=caption
    )
    
    return {
        "success": True,
        "message": "Media attached to report",
        "report_media_id": report_media.id
    }


@router.get("/my-media", response_model=MediaListResponse)
async def get_my_media(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    file_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's uploaded media
    
    - Paginated results
    - Optional filter by file_type
    """
    query = db.query(MediaFile).filter(MediaFile.user_id == current_user.id)
    
    if file_type:
        query = query.filter(MediaFile.file_type == file_type)
    
    total = query.count()
    media_list = query.order_by(MediaFile.created_at.desc()).offset(skip).limit(limit).all()
    
    return MediaListResponse(
        total=total,
        media=[MediaResponse.from_orm(m) for m in media_list]
    )
