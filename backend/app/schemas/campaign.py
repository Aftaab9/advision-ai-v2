from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class CampaignBase(BaseModel):
    name: str
    platform: str
    country: Optional[str] = None
    product_category: Optional[str] = None
    spend: Optional[Decimal] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    conversions: Optional[int] = None
    reach: Optional[int] = None
    revenue: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignOut(CampaignBase):
    id: UUID
    organization_id: UUID
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
