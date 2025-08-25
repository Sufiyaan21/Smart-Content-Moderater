from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.base import get_db
from app.models.models import ModerationRequest, ModerationResult, NotificationLog, ModerationStatus, NotificationChannel, NotificationStatus
from app.schemas.schemas import (
    TextModerationRequest as TextRequest,
    ImageModerationRequest as ImageRequest,
    TextModerationResponse,
    ImageModerationResponse,
    ErrorResponse
)
from app.services.llm_service import llm_service
from app.services.image_service import image_service
from app.services.notification_service import notification_service
from app.utils.hashing import hash_text, hash_image, hash_url
from app.core.logger import get_logger
from app.models.models import ContentType

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/moderate", tags=["moderation"])


@router.post("/text", response_model=TextModerationResponse)
async def moderate_text(
    request: TextRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> TextModerationResponse:
    """
    Analyze text content for inappropriate material.
    
    Args:
        request: Text moderation request
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Text moderation response with classification results
    """
    try:
        logger.info("Text moderation request received", email=request.email, text_length=len(request.text))
        
        # Generate content hash
        content_hash = hash_text(request.text)
        
        # Check for duplicate content
        existing_request = db.query(ModerationRequest).filter(
            ModerationRequest.content_hash == content_hash,
            ModerationRequest.content_type == ContentType.TEXT
        ).first()
        
        if existing_request:
            logger.info("Duplicate content found, returning existing result", 
                       request_id=existing_request.id, content_hash=content_hash)
            
            # Get the latest result
            latest_result = db.query(ModerationResult).filter(
                ModerationResult.request_id == existing_request.id
            ).order_by(ModerationResult.created_at.desc()).first()
            
            if latest_result:
                return TextModerationResponse(
                    success=True,
                    request_id=existing_request.id,
                    classification=latest_result.classification,
                    confidence=latest_result.confidence,
                    reasoning=latest_result.reasoning,
                    message="Content analyzed successfully (cached result)"
                )
        
        # Create moderation request
        moderation_request = ModerationRequest(
            email=request.email,
            content_type=ContentType.TEXT,
            content_hash=content_hash,
            status=ModerationStatus.PROCESSING
        )
        db.add(moderation_request)
        db.commit()
        db.refresh(moderation_request)
        
        # Analyze text with LLM
        llm_result = await llm_service.moderate_text(request.text)
        
        # Create moderation result
        moderation_result = ModerationResult(
            request_id=moderation_request.id,
            classification=llm_result['classification'],
            confidence=llm_result['confidence'],
            reasoning=llm_result['reasoning'],
            llm_response=llm_result['llm_response']
        )
        db.add(moderation_result)
        
        # Update request status
        moderation_request.status = ModerationStatus.COMPLETED
        db.commit()
        
        # Send notifications in background if content is flagged
        if llm_result['flagged']:
            background_tasks.add_task(
                send_notifications_background,
                moderation_request.id,
                request.email,
                llm_result['classification'],
                'text',
                request.text[:200],
                llm_result['confidence'],
                llm_result['reasoning']
            )
        
        logger.info("Text moderation completed", 
                   request_id=moderation_request.id,
                   classification=llm_result['classification'],
                   confidence=llm_result['confidence'])
        
        return TextModerationResponse(
            success=True,
            request_id=moderation_request.id,
            classification=llm_result['classification'],
            confidence=llm_result['confidence'],
            reasoning=llm_result['reasoning'],
            message="Content analyzed successfully"
        )
        
    except Exception as e:
        logger.error("Error in text moderation", error=str(e), email=request.email)
        
        # Update request status to failed if it was created
        if 'moderation_request' in locals():
            moderation_request.status = ModerationStatus.FAILED
            db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze text content: {str(e)}"
        )


@router.post("/image", response_model=ImageModerationResponse)
async def moderate_image(
    request: ImageRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ImageModerationResponse:
    """
    Analyze image content for inappropriate material.
    
    Args:
        request: Image moderation request
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Image moderation response with classification results
    """
    try:
        logger.info("Image moderation request received", email=request.email)
        
        # Process image
        if request.image_url:
            image_bytes, mime_type = await image_service.process_image(image_url=request.image_url)
            content_hash = hash_url(request.image_url)
            content_preview = f"Image from URL: {request.image_url}"
        elif request.image_base64:
            image_bytes, mime_type = await image_service.process_image(image_base64=request.image_base64)
            content_hash = hash_image(request.image_base64)
            content_preview = "Image from base64 data"
        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 must be provided")
        
        # Check for duplicate content
        existing_request = db.query(ModerationRequest).filter(
            ModerationRequest.content_hash == content_hash,
            ModerationRequest.content_type == ContentType.IMAGE
        ).first()
        
        if existing_request:
            logger.info("Duplicate content found, returning existing result", 
                       request_id=existing_request.id, content_hash=content_hash)
            
            # Get the latest result
            latest_result = db.query(ModerationResult).filter(
                ModerationResult.request_id == existing_request.id
            ).order_by(ModerationResult.created_at.desc()).first()
            
            if latest_result:
                return ImageModerationResponse(
                    success=True,
                    request_id=existing_request.id,
                    classification=latest_result.classification,
                    confidence=latest_result.confidence,
                    reasoning=latest_result.reasoning,
                    message="Content analyzed successfully (cached result)"
                )
        
        # Create moderation request
        moderation_request = ModerationRequest(
            email=request.email,
            content_type=ContentType.IMAGE,
            content_hash=content_hash,
            status=ModerationStatus.PROCESSING
        )
        db.add(moderation_request)
        db.commit()
        db.refresh(moderation_request)
        
        # Analyze image with LLM
        llm_result = await llm_service.moderate_image(image_bytes, content_preview)
        
        # Create moderation result
        moderation_result = ModerationResult(
            request_id=moderation_request.id,
            classification=llm_result['classification'],
            confidence=llm_result['confidence'],
            reasoning=llm_result['reasoning'],
            llm_response=llm_result['llm_response']
        )
        db.add(moderation_result)
        
        # Update request status
        moderation_request.status = ModerationStatus.COMPLETED
        db.commit()
        
        # Send notifications in background if content is flagged
        if llm_result['flagged']:
            background_tasks.add_task(
                send_notifications_background,
                moderation_request.id,
                request.email,
                llm_result['classification'],
                'image',
                content_preview,
                llm_result['confidence'],
                llm_result['reasoning']
            )
        
        logger.info("Image moderation completed", 
                   request_id=moderation_request.id,
                   classification=llm_result['classification'],
                   confidence=llm_result['confidence'])
        
        return ImageModerationResponse(
            success=True,
            request_id=moderation_request.id,
            classification=llm_result['classification'],
            confidence=llm_result['confidence'],
            reasoning=llm_result['reasoning'],
            message="Content analyzed successfully"
        )
        
    except Exception as e:
        logger.error("Error in image moderation", error=str(e), email=request.email)
        
        # Update request status to failed if it was created
        if 'moderation_request' in locals():
            moderation_request.status = ModerationStatus.FAILED
            db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze image content: {str(e)}"
        )


async def send_notifications_background(
    request_id: int,
    email: str,
    classification: Any,
    content_type: str,
    content_preview: str,
    confidence: float,
    reasoning: str
):
    """
    Background task to send notifications.
    
    Args:
        request_id: Moderation request ID
        email: User email
        classification: Content classification
        content_type: Type of content
        content_preview: Preview of content
        confidence: Confidence score
        reasoning: Reasoning for classification
    """
    try:
        from app.db.base import SessionLocal
        
        db = SessionLocal()
        
        # Send notifications
        notification_results = await notification_service.send_notifications(
            request_id, email, classification, content_type, content_preview, confidence, reasoning
        )
        
        # Log notification results
        for channel, result in notification_results.items():
            notification_log = NotificationLog(
                request_id=request_id,
                channel=NotificationChannel.SLACK if channel == 'slack' else NotificationChannel.EMAIL,
                status=NotificationStatus.SENT if result.get('status') == 'sent' else NotificationStatus.FAILED,
                error_message=result.get('error'),
                sent_at=db.query(ModerationRequest).filter(ModerationRequest.id == request_id).first().created_at
            )
            db.add(notification_log)
        
        db.commit()
        db.close()
        
        logger.info("Background notifications completed", request_id=request_id, results=notification_results)
        
    except Exception as e:
        logger.error("Error in background notifications", error=str(e), request_id=request_id)



