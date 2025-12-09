from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    EXCEL = "excel"


class Document(Base):
    """Documents uploaded for RAG analysis"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Document Info
    name = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_url = Column(String(500))  # R2/S3 URL
    file_size = Column(Integer)  # bytes
    
    # Processing
    is_processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSONB)  # Additional metadata (author, date, etc.)
    
    # Vector DB
    chroma_namespace = Column(String(100))  # Unique namespace in Chroma
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
