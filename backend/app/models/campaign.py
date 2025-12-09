from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False, index=True)  # instagram, facebook, youtube, google_ads
    country = Column(String(10))
    product_category = Column(String(100))
    
    # Metrics
    spend = Column(DECIMAL(12, 2))
    impressions = Column(Integer)
    clicks = Column(Integer)
    conversions = Column(Integer)
    reach = Column(Integer)
    revenue = Column(DECIMAL(12, 2))
    
    # Dates
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Status
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    creatives = relationship("Creative", back_populates="campaign", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="campaign", cascade="all, delete-orphan")
    trust_score = relationship("TrustScore", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    bot_analysis = relationship("BotAnalysis", back_populates="campaign", cascade="all, delete-orphan")
    bias_audits = relationship("BiasAudit", back_populates="campaign", cascade="all, delete-orphan")
