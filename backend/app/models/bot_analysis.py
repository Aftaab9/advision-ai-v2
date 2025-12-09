from sqlalchemy import Column, Float, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class BotAnalysis(Base):
    __tablename__ = "bot_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), index=True)
    
    # Analysis Results
    bot_probability = Column(DECIMAL(5, 4), nullable=False)  # 0.0000 to 1.0000
    red_flags = Column(JSONB)  # ["rapid_actions", "generic_comments", "suspicious_timing"]
    engagement_graph_data = Column(JSONB)  # Graph structure for GNN analysis
    
    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="bot_analysis")
