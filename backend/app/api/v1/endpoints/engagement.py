# Copyright (c) 2025 CityLens Contributors
# Licensed under the GNU General Public License v3.0 (GPL-3.0)

"""
Comment, Vote, Follow endpoints - User engagement features
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.postgres import get_db
from app.models.report import ReportComment, ReportVote, ReportFollower, Report
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate, CommentListResponse

router = APIRouter()


# ============================================
# COMMENT ENDPOINTS
# ============================================

@router.post("/reports/{report_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    report_id: int = Path(..., description="Report ID"),
    comment_in: CommentCreate = ...,
    user_id: int = Query(..., description="User ID (temporary, will use auth)"),
    db: Session = Depends(get_db)
):
    """
    Thêm bình luận vào báo cáo
    
    - **report_id**: ID báo cáo
    - **content**: Nội dung bình luận (1-1000 ký tự)
    - **parent_id**: ID comment cha (nếu reply)
    - **images**: Danh sách URL hình ảnh (optional)
    """
    # Check report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check parent comment exists (if replying)
    if comment_in.parent_id:
        parent = db.query(ReportComment).filter(
            and_(
                ReportComment.id == comment_in.parent_id,
                ReportComment.report_id == report_id
            )
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
    
    # Create comment
    comment = ReportComment(
        report_id=report_id,
        user_id=user_id,
        parent_id=comment_in.parent_id,
        content=comment_in.content,
        images=comment_in.images or []
    )
    
    db.add(comment)
    
    # Update report comments count
    report.comments_count = db.query(func.count(ReportComment.id)).filter(
        ReportComment.report_id == report_id
    ).scalar()
    
    db.commit()
    db.refresh(comment)
    
    # TODO: Send notification to report owner and parent comment author
    
    return comment


@router.get("/reports/{report_id}/comments", response_model=CommentListResponse)
async def get_report_comments(
    report_id: int = Path(..., description="Report ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    parent_id: Optional[int] = Query(None, description="Filter by parent comment"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bình luận của báo cáo
    
    - **report_id**: ID báo cáo
    - **parent_id**: Lọc theo comment cha (None = root comments only)
    - **skip**: Phân trang
    - **limit**: Số lượng tối đa
    """
    query = db.query(ReportComment).filter(ReportComment.report_id == report_id)
    
    # Filter by parent_id
    if parent_id is None:
        # Get root comments only
        query = query.filter(ReportComment.parent_id.is_(None))
    else:
        # Get replies to specific comment
        query = query.filter(ReportComment.parent_id == parent_id)
    
    total = query.count()
    
    comments = query.order_by(ReportComment.created_at.asc()).offset(skip).limit(limit).all()
    
    # Enrich with user info (TODO: optimize with join)
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        if user:
            comment.user_name = user.full_name or user.username
            comment.user_avatar = user.avatar_url
        
        # Count replies
        comment.replies_count = db.query(func.count(ReportComment.id)).filter(
            ReportComment.parent_id == comment.id
        ).scalar()
    
    return {
        "comments": comments,
        "total": total
    }


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int = Path(..., description="Comment ID"),
    comment_update: CommentUpdate = ...,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Cập nhật bình luận (chỉ owner mới được sửa)
    
    - **comment_id**: ID bình luận
    - **content**: Nội dung mới
    """
    comment = db.query(ReportComment).filter(
        and_(
            ReportComment.id == comment_id,
            ReportComment.user_id == user_id  # Verify ownership
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or unauthorized"
        )
    
    comment.content = comment_update.content
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int = Path(..., description="Comment ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Xóa bình luận (chỉ owner hoặc admin)
    
    - **comment_id**: ID bình luận
    """
    comment = db.query(ReportComment).filter(
        and_(
            ReportComment.id == comment_id,
            ReportComment.user_id == user_id  # Verify ownership (TODO: allow admin)
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or unauthorized"
        )
    
    report_id = comment.report_id
    
    db.delete(comment)
    
    # Update report comments count
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        report.comments_count = db.query(func.count(ReportComment.id)).filter(
            ReportComment.report_id == report_id
        ).scalar()
    
    db.commit()
    
    return None


# ============================================
# VOTE ENDPOINTS
# ============================================

@router.post("/reports/{report_id}/vote", status_code=status.HTTP_201_CREATED)
async def vote_report(
    report_id: int = Path(..., description="Report ID"),
    vote_type: str = Query(..., pattern="^(upvote|downvote)$", description="Vote type"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Vote (upvote/downvote) cho báo cáo
    
    - **report_id**: ID báo cáo
    - **vote_type**: "upvote" hoặc "downvote"
    
    Nếu user đã vote trước đó, vote cũ sẽ bị thay thế
    """
    # Check report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check existing vote
    existing_vote = db.query(ReportVote).filter(
        and_(
            ReportVote.report_id == report_id,
            ReportVote.user_id == user_id
        )
    ).first()
    
    if existing_vote:
        # Update vote type
        old_type = existing_vote.vote_type
        existing_vote.vote_type = vote_type
        
        # Update report counts
        if old_type == "upvote" and vote_type == "downvote":
            report.upvotes = max(0, report.upvotes - 1)
            report.downvotes += 1
        elif old_type == "downvote" and vote_type == "upvote":
            report.downvotes = max(0, report.downvotes - 1)
            report.upvotes += 1
    else:
        # Create new vote
        vote = ReportVote(
            report_id=report_id,
            user_id=user_id,
            vote_type=vote_type
        )
        db.add(vote)
        
        # Update report counts
        if vote_type == "upvote":
            report.upvotes += 1
        else:
            report.downvotes += 1
    
    db.commit()
    
    # TODO: Send notification to report owner (if upvote)
    
    return {
        "status": "success",
        "vote_type": vote_type,
        "upvotes": report.upvotes,
        "downvotes": report.downvotes
    }


@router.delete("/reports/{report_id}/vote", status_code=status.HTTP_204_NO_CONTENT)
async def remove_vote(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Xóa vote của user cho báo cáo
    
    - **report_id**: ID báo cáo
    """
    vote = db.query(ReportVote).filter(
        and_(
            ReportVote.report_id == report_id,
            ReportVote.user_id == user_id
        )
    ).first()
    
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )
    
    # Update report counts
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        if vote.vote_type == "upvote":
            report.upvotes = max(0, report.upvotes - 1)
        else:
            report.downvotes = max(0, report.downvotes - 1)
    
    db.delete(vote)
    db.commit()
    
    return None


@router.get("/reports/{report_id}/votes")
async def get_report_votes(
    report_id: int = Path(..., description="Report ID"),
    db: Session = Depends(get_db)
):
    """
    Lấy thống kê votes của báo cáo
    
    - **report_id**: ID báo cáo
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {
        "report_id": report_id,
        "upvotes": report.upvotes,
        "downvotes": report.downvotes,
        "total": report.upvotes + report.downvotes
    }


@router.get("/reports/{report_id}/my-vote")
async def get_my_vote(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Kiểm tra vote của user cho báo cáo
    
    - **report_id**: ID báo cáo
    
    Returns null nếu chưa vote
    """
    vote = db.query(ReportVote).filter(
        and_(
            ReportVote.report_id == report_id,
            ReportVote.user_id == user_id
        )
    ).first()
    
    if not vote:
        return {"vote_type": None}
    
    return {"vote_type": vote.vote_type}


# ============================================
# FOLLOW ENDPOINTS
# ============================================

@router.post("/reports/{report_id}/follow", status_code=status.HTTP_201_CREATED)
async def follow_report(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Theo dõi báo cáo (nhận thông báo khi có cập nhật)
    
    - **report_id**: ID báo cáo
    """
    # Check report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check already following
    existing = db.query(ReportFollower).filter(
        and_(
            ReportFollower.report_id == report_id,
            ReportFollower.user_id == user_id
        )
    ).first()
    
    if existing:
        return {
            "status": "already_following",
            "message": "Already following this report"
        }
    
    # Create follower
    follower = ReportFollower(
        report_id=report_id,
        user_id=user_id
    )
    
    db.add(follower)
    db.commit()
    
    return {
        "status": "success",
        "message": "Now following this report"
    }


@router.delete("/reports/{report_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_report(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Bỏ theo dõi báo cáo
    
    - **report_id**: ID báo cáo
    """
    follower = db.query(ReportFollower).filter(
        and_(
            ReportFollower.report_id == report_id,
            ReportFollower.user_id == user_id
        )
    ).first()
    
    if not follower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this report"
        )
    
    db.delete(follower)
    db.commit()
    
    return None


@router.get("/reports/{report_id}/is-following")
async def check_following(
    report_id: int = Path(..., description="Report ID"),
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Kiểm tra user có đang follow báo cáo không
    
    - **report_id**: ID báo cáo
    """
    follower = db.query(ReportFollower).filter(
        and_(
            ReportFollower.report_id == report_id,
            ReportFollower.user_id == user_id
        )
    ).first()
    
    return {
        "is_following": follower is not None
    }


@router.get("/my-follows")
async def get_my_followed_reports(
    user_id: int = Query(..., description="User ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách báo cáo user đang follow
    
    - **skip**: Phân trang
    - **limit**: Số lượng tối đa
    """
    query = db.query(ReportFollower).filter(ReportFollower.user_id == user_id)
    
    total = query.count()
    
    followers = query.order_by(ReportFollower.created_at.desc()).offset(skip).limit(limit).all()
    
    # Get report details
    report_ids = [f.report_id for f in followers]
    reports = db.query(Report).filter(Report.id.in_(report_ids)).all()
    
    return {
        "reports": reports,
        "total": total
    }
