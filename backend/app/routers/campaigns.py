from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Campaign
from ..schemas.campaign import CampaignCreate, CampaignOut
from .auth import oauth2_scheme
from ..utils.security import decode_access_token

router = APIRouter()


def get_current_user_data(token: str = Depends(oauth2_scheme)):
    """Extract user data from token"""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return payload


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Create a new campaign"""
    
    campaign = Campaign(
        **campaign_data.dict(),
        organization_id=current_user["org_id"]
    )
    
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    return campaign


@router.get("/", response_model=List[CampaignOut])
async def list_campaigns(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data),
    skip: int = 0,
    limit: int = 100
):
    """List all campaigns for the organization"""
    
    campaigns = db.query(Campaign).filter(
        Campaign.organization_id == current_user["org_id"]
    ).offset(skip).limit(limit).all()
    
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Get a specific campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Delete a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    db.delete(campaign)
    db.commit()
    
    return None
