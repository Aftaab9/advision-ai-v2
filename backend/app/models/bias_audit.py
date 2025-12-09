from sqlalchemy import Column, Boolean, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class BiasAudit(Base):
    __tablename__ = "bias_audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    
    # Fairness Metrics
    demographic_parity = Column(DECIMAL(5, 4))
    equalized_odds = Column(DECIMAL(5, 4))
    disparate_impact_ratio = Column(DECIMAL(5, 4))
    
    # Detailed Results
    bias_report = Column(JSONB)  # Detailed breakdown by demographic group
    flagged = Column(Boolean, default=False)
    
    # Timestamps
    audited_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="bias_audits")
