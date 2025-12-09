from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    creative_id = Column(UUID(as_uuid=True), ForeignKey("creatives.id", ondelete="SET NULL"))
    
    # Prediction Type
    prediction_type = Column(String(50), nullable=False, index=True)
    # Types: engagement, roi, quality, semantic_relevance, emotion, fatigue, bot, attribution
    
    # Model Info
    model_version = Column(String(50), nullable=False)
    
    # Predictions (flexible JSONB)
    predictions = Column(JSONB, nullable=False)
    # Examples:
    # {"engagement_rate": 0.045, "confidence": 0.87}
    # {"roi": 2.3, "cac": 45.2, "clv": 320.5}
    # {"quality_score": 78, "suggestions": ["increase contrast"]}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="predictions")
    creative = relationship("Creative", back_populates="predictions")
