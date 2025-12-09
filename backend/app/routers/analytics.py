from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..models import Campaign
from ..services.analytics import AnalyticsService
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


@router.get("/dashboard")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Get dashboard statistics"""
    
    stats = AnalyticsService.calculate_dashboard_stats(db, current_user["org_id"])
    return stats


@router.get("/campaign/{campaign_id}/roi")
async def get_campaign_roi(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Get ROI metrics for a specific campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    roi_metrics = AnalyticsService.calculate_roi_metrics(campaign)
    return roi_metrics


@router.post("/simulate-budget")
async def simulate_budget(
    campaign_id: UUID,
    new_spend: float,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Simulate budget changes and predict impact"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Simple simulation: scale metrics proportionally
    current_spend = float(campaign.spend or 1)
    scale_factor = new_spend / current_spend
    
    simulated = {
        "current": {
            "spend": float(campaign.spend or 0),
            "impressions": campaign.impressions or 0,
            "clicks": campaign.clicks or 0,
            "conversions": campaign.conversions or 0,
            "revenue": float(campaign.revenue or 0)
        },
        "simulated": {
            "spend": new_spend,
            "impressions": int((campaign.impressions or 0) * scale_factor),
            "clicks": int((campaign.clicks or 0) * scale_factor),
            "conversions": int((campaign.conversions or 0) * scale_factor),
            "revenue": float(campaign.revenue or 0) * scale_factor
        }
    }
    
    # Calculate ROI for both
    current_roi = ((simulated["current"]["revenue"] - simulated["current"]["spend"]) / simulated["current"]["spend"] * 100) if simulated["current"]["spend"] > 0 else 0
    simulated_roi = ((simulated["simulated"]["revenue"] - simulated["simulated"]["spend"]) / simulated["simulated"]["spend"] * 100) if simulated["simulated"]["spend"] > 0 else 0
    
    simulated["current"]["roi"] = round(current_roi, 2)
    simulated["simulated"]["roi"] = round(simulated_roi, 2)
    simulated["roi_change"] = round(simulated_roi - current_roi, 2)
    
    return simulated
