from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.models import ContentType, ModerationStatus, ClassificationType, NotificationChannel, NotificationStatus


# Request Schemas
class TextModerationRequest(BaseModel):
    email: EmailStr
    text: str = Field(..., min_length=1, max_length=10000, description="Text content to moderate")


class ImageModerationRequest(BaseModel):
    email: EmailStr
    image_url: Optional[str] = Field(None, description="URL of the image to moderate")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")


# Response Schemas
class ModerationResultResponse(BaseModel):
    id: int
    classification: ClassificationType
    confidence: float
    reasoning: Optional[str]
    llm_response: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModerationRequestResponse(BaseModel):
    id: int
    email: str
    content_type: ContentType
    content_hash: str
    status: ModerationStatus
    created_at: datetime
    results: List[ModerationResultResponse] = []
    
    class Config:
        from_attributes = True


class NotificationLogResponse(BaseModel):
    id: int
    channel: NotificationChannel
    status: NotificationStatus
    error_message: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TextModerationResponse(BaseModel):
    success: bool
    request_id: int
    classification: ClassificationType
    confidence: float
    reasoning: Optional[str]
    message: str


class ImageModerationResponse(BaseModel):
    success: bool
    request_id: int
    classification: ClassificationType
    confidence: float
    reasoning: Optional[str]
    message: str


# Analytics Schemas
class UserAnalyticsSummary(BaseModel):
    email: str
    total_requests: int
    text_requests: int
    image_requests: int
    safe_content: int
    flagged_content: int
    toxic_content: int
    spam_content: int
    harassment_content: int
    inappropriate_content: int
    average_confidence: float
    last_request_date: Optional[datetime]


class AnalyticsResponse(BaseModel):
    success: bool
    data: UserAnalyticsSummary
    message: str


# Error Schemas
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    details: Optional[dict] = None


# Health Check Schema
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"



