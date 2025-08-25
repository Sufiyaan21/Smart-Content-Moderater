from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from app.db.base import get_db
from app.models.models import ModerationRequest, ModerationResult, ClassificationType, ContentType
from app.schemas.schemas import AnalyticsResponse, UserAnalyticsSummary, ErrorResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsResponse)
async def get_user_analytics_summary(
    user: str = Query(..., description="User email address"),
    db: Session = Depends(get_db)
) -> AnalyticsResponse:
    """
    Get analytics summary for a specific user.
    
    Args:
        user: User email address
        db: Database session
        
    Returns:
        Analytics summary for the user
    """
    try:
        logger.info("Analytics summary request received", user=user)
        
        # Get all requests for the user
        user_requests = db.query(ModerationRequest).filter(
            ModerationRequest.email == user
        ).all()
        
        if not user_requests:
            # Return empty summary for user with no requests
            return AnalyticsResponse(
                success=True,
                data=UserAnalyticsSummary(
                    email=user,
                    total_requests=0,
                    text_requests=0,
                    image_requests=0,
                    safe_content=0,
                    flagged_content=0,
                    toxic_content=0,
                    spam_content=0,
                    harassment_content=0,
                    inappropriate_content=0,
                    average_confidence=0.0,
                    last_request_date=None
                ),
                message="No moderation requests found for this user"
            )
        
        # Get request IDs
        request_ids = [req.id for req in user_requests]
        
        # Get results for all requests
        results = db.query(ModerationResult).filter(
            ModerationResult.request_id.in_(request_ids)
        ).all()
        
        # Calculate analytics
        total_requests = len(user_requests)
        text_requests = len([req for req in user_requests if req.content_type == ContentType.TEXT])
        image_requests = len([req for req in user_requests if req.content_type == ContentType.IMAGE])
        
        # Count classifications
        safe_content = len([r for r in results if r.classification == ClassificationType.SAFE])
        toxic_content = len([r for r in results if r.classification == ClassificationType.TOXIC])
        spam_content = len([r for r in results if r.classification == ClassificationType.SPAM])
        harassment_content = len([r for r in results if r.classification == ClassificationType.HARASSMENT])
        inappropriate_content = len([r for r in results if r.classification == ClassificationType.INAPPROPRIATE])
        
        flagged_content = total_requests - safe_content
        
        # Calculate average confidence
        if results:
            average_confidence = sum(r.confidence for r in results) / len(results)
        else:
            average_confidence = 0.0
        
        # Get last request date
        last_request = max(user_requests, key=lambda x: x.created_at)
        last_request_date = last_request.created_at
        
        # Create analytics summary
        analytics_summary = UserAnalyticsSummary(
            email=user,
            total_requests=total_requests,
            text_requests=text_requests,
            image_requests=image_requests,
            safe_content=safe_content,
            flagged_content=flagged_content,
            toxic_content=toxic_content,
            spam_content=spam_content,
            harassment_content=harassment_content,
            inappropriate_content=inappropriate_content,
            average_confidence=round(average_confidence, 3),
            last_request_date=last_request_date
        )
        
        logger.info("Analytics summary generated", 
                   user=user, 
                   total_requests=total_requests,
                   flagged_content=flagged_content)
        
        return AnalyticsResponse(
            success=True,
            data=analytics_summary,
            message="Analytics summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error("Error generating analytics summary", error=str(e), user=user)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics summary: {str(e)}"
        )


@router.get("/summary/all", response_model=dict)
async def get_all_users_analytics_summary(
    db: Session = Depends(get_db)
) -> dict:
    """
    Get analytics summary for all users.
    
    Args:
        db: Database session
        
    Returns:
        Analytics summary for all users
    """
    try:
        logger.info("All users analytics summary request received")
        
        # Get all unique users
        users = db.query(ModerationRequest.email).distinct().all()
        user_emails = [user[0] for user in users]
        
        # Get analytics for each user
        all_analytics = {}
        for email in user_emails:
            try:
                # Reuse the single user analytics logic
                user_requests = db.query(ModerationRequest).filter(
                    ModerationRequest.email == email
                ).all()
                
                if not user_requests:
                    continue
                
                request_ids = [req.id for req in user_requests]
                results = db.query(ModerationResult).filter(
                    ModerationResult.request_id.in_(request_ids)
                ).all()
                
                # Calculate analytics
                total_requests = len(user_requests)
                text_requests = len([req for req in user_requests if req.content_type == ContentType.TEXT])
                image_requests = len([req for req in user_requests if req.content_type == ContentType.IMAGE])
                
                safe_content = len([r for r in results if r.classification == ClassificationType.SAFE])
                toxic_content = len([r for r in results if r.classification == ClassificationType.TOXIC])
                spam_content = len([r for r in results if r.classification == ClassificationType.SPAM])
                harassment_content = len([r for r in results if r.classification == ClassificationType.HARASSMENT])
                inappropriate_content = len([r for r in results if r.classification == ClassificationType.INAPPROPRIATE])
                
                flagged_content = total_requests - safe_content
                
                if results:
                    average_confidence = sum(r.confidence for r in results) / len(results)
                else:
                    average_confidence = 0.0
                
                last_request = max(user_requests, key=lambda x: x.created_at)
                
                all_analytics[email] = {
                    "total_requests": total_requests,
                    "text_requests": text_requests,
                    "image_requests": image_requests,
                    "safe_content": safe_content,
                    "flagged_content": flagged_content,
                    "toxic_content": toxic_content,
                    "spam_content": spam_content,
                    "harassment_content": harassment_content,
                    "inappropriate_content": inappropriate_content,
                    "average_confidence": round(average_confidence, 3),
                    "last_request_date": last_request.created_at.isoformat()
                }
                
            except Exception as e:
                logger.error("Error processing analytics for user", user=email, error=str(e))
                continue
        
        # Calculate overall statistics
        total_users = len(all_analytics)
        total_requests_all = sum(data["total_requests"] for data in all_analytics.values())
        total_flagged_all = sum(data["flagged_content"] for data in all_analytics.values())
        
        overall_stats = {
            "total_users": total_users,
            "total_requests": total_requests_all,
            "total_flagged_content": total_flagged_all,
            "flag_rate": round(total_flagged_all / total_requests_all * 100, 2) if total_requests_all > 0 else 0
        }
        
        logger.info("All users analytics summary generated", 
                   total_users=total_users,
                   total_requests=total_requests_all,
                   total_flagged=total_flagged_all)
        
        return {
            "success": True,
            "overall_stats": overall_stats,
            "user_analytics": all_analytics,
            "message": "All users analytics summary retrieved successfully"
        }
        
    except Exception as e:
        logger.error("Error generating all users analytics summary", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate all users analytics summary: {str(e)}"
        )



