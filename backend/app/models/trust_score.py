from sqlalchemy import Column, Float, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class TrustScore(Base):
    """AI Justice Score - Comprehensive trust scoring for campaigns"""
    __tablename__ = "trust_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Overall Score (0-100)
    trust_score = Column(DECIMAL(5, 2), nullable=False)  # 0.00 to 100.00
    
    # Component Scores (0-1)
    authenticity_score = Column(Float)  # Is content genuine?
    factual_accuracy_score = Column(Float)  # Are claims verifiable?
    source_credibility_score = Column(Float)  # Are sources trustworthy?
    transparency_score = Column(Float)  # Is AI usage disclosed?
    ethical_compliance_score = Column(Float)  # Follows advertising ethics?
    
    # AI Detection Results
    ai_text_probability = Column(Float)  # 0-1, probability text is AI-generated
    ai_image_probability = Column(Float)  # 0-1, probability image is AI-generated
    
    # Fact-Checking
    fact_check_results = Column(JSONB)  # Detailed fact-check findings
    # Example: [{"claim": "...", "verdict": "true/false/mixed", "source": "..."}]
    
    # Recommendations
    recommendations = Column(JSONB)  # List of improvement suggestions
    # Example: ["Verify claim X", "Disclose AI usage", "Add credible sources"]
    
    # Badge Level
    badge_level = Column(Text)  # "high" (90-100), "medium" (70-89), "low" (50-69), "risk" (0-49)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="trust_score")
