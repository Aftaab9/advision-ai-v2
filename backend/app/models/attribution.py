from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class AttributionTouchpoint(Base):
    __tablename__ = "attribution_touchpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversion Grouping
    conversion_id = Column(String(255), nullable=False, index=True)  # Groups touchpoints for one conversion
    
    # Touchpoint Details
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="SET NULL"))
    channel = Column(String(50), nullable=False)
    touchpoint_timestamp = Column(DateTime(timezone=True), nullable=False)
    position_in_path = Column(Integer, nullable=False)  # 1 = first touch, N = last touch
    
    # Attribution Score (calculated by ML model)
    attribution_score = Column(DECIMAL(5, 4))  # 0.0000 to 1.0000
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
