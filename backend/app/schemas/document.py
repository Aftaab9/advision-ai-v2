from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DocumentCreate(BaseModel):
    title: str
    content: str
    document_type: str = "knowledge_base"
    source_url: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: int
    organization_id: int
    title: str
    content: str
    document_type: str
    source_url: Optional[str]
    metadata_: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
