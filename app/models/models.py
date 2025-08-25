from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ContentType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"


class ModerationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ClassificationType(str, enum.Enum):
    SAFE = "safe"
    TOXIC = "toxic"
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"


class NotificationChannel(str, enum.Enum):
    SLACK = "slack"
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class ModerationRequest(Base):
    __tablename__ = "moderation_requests"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    content_type = Column(Enum(ContentType), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    status = Column(Enum(ModerationStatus), default=ModerationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    results = relationship(
        "ModerationResult", back_populates="request", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "NotificationLog", back_populates="request", cascade="all, delete-orphan"
    )


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    classification = Column(Enum(ClassificationType), nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=True)
    llm_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    request = relationship("ModerationRequest", back_populates="results")


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("moderation_requests.id"), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    request = relationship("ModerationRequest", back_populates="notifications")




