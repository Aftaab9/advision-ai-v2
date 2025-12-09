from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class CreativeType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    CAROUSEL = "carousel"


class CreativeFormat(str, enum.Enum):
    SQUARE = "square"
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    STORY = "story"


class Creative(Base):
    __tablename__ = "creatives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    
    # Content
    ad_text = Column(Text)
    image_url = Column(String(500))  # R2/S3 URL
    video_url = Column(String(500))  # R2/S3 URL
    
    # Metadata
    creative_type = Column(Enum(CreativeType))
    format = Column(Enum(CreativeFormat))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="creatives")
    predictions = relationship("Prediction", back_populates="creative", cascade="all, delete-orphan")
