from sqlalchemy import Column, String, Integer, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from ..database import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model Info
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    s3_path = Column(String(500), nullable=False)
    
    # Metadata
    training_date = Column(DateTime(timezone=True))
    dataset_size = Column(Integer)
    evaluation_metrics = Column(JSONB)  # {"mape": 0.12, "r2": 0.85}
    
    # Deployment
    is_active = Column(Boolean, default=False, index=True)
    deployed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('model_name', 'version', name='uq_model_version'),
    )
