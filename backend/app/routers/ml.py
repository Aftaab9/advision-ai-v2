from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from ..database import get_db
from ..models import Campaign, Creative, Prediction, TrustScore
from ..services.ml_client import ml_client
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


@router.post("/predict-engagement/{campaign_id}")
async def predict_engagement(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Predict engagement for a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Prepare data for ML service
    campaign_data = {
        "platform": campaign.platform,
        "country": campaign.country,
        "product_category": campaign.product_category,
        "spend": float(campaign.spend or 0),
        "impressions": campaign.impressions or 0,
        "reach": campaign.reach or 0
    }
    
    try:
        # Call ML service
        result = await ml_client.predict_engagement(campaign_data)
        
        # Store prediction
        prediction = Prediction(
            organization_id=current_user["org_id"],
            campaign_id=campaign_id,
            prediction_type="engagement",
            model_version="baseline-v1",
            predictions=result
        )
        db.add(prediction)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML service error: {str(e)}"
        )


@router.post("/trust-score/{campaign_id}")
async def calculate_trust_score(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Calculate AI Justice Score (Trust Score) for a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.organization_id == current_user["org_id"]
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Get creative for analysis
    creative = db.query(Creative).filter(Creative.campaign_id == campaign_id).first()
    
    try:
        # Call ML service for trust score calculation
        result = await ml_client.calculate_trust_score(
            campaign_id=str(campaign_id),
            text=creative.ad_text if creative else None,
            image_url=creative.image_url if creative else None
        )
        
        # Store or update trust score
        trust_score = db.query(TrustScore).filter(TrustScore.campaign_id == campaign_id).first()
        
        if trust_score:
            # Update existing
            trust_score.trust_score = result["trust_score"]
            trust_score.authenticity_score = result.get("authenticity_score")
            trust_score.factual_accuracy_score = result.get("factual_accuracy_score")
            trust_score.ai_text_probability = result.get("ai_text_probability")
            trust_score.ai_image_probability = result.get("ai_image_probability")
            trust_score.badge_level = result.get("badge_level")
        else:
            # Create new
            trust_score = TrustScore(
                organization_id=current_user["org_id"],
                campaign_id=campaign_id,
                trust_score=result["trust_score"],
                authenticity_score=result.get("authenticity_score"),
                factual_accuracy_score=result.get("factual_accuracy_score"),
                ai_text_probability=result.get("ai_text_probability"),
                ai_image_probability=result.get("ai_image_probability"),
                badge_level=result.get("badge_level"),
                fact_check_results=result.get("fact_check_results"),
                recommendations=result.get("recommendations")
            )
            db.add(trust_score)
        
        db.commit()
        db.refresh(trust_score)
        
        return {
            "trust_score": float(trust_score.trust_score),
            "badge_level": trust_score.badge_level,
            "authenticity_score": trust_score.authenticity_score,
            "ai_text_probability": trust_score.ai_text_probability,
            "ai_image_probability": trust_score.ai_image_probability,
            "recommendations": trust_score.recommendations
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML service error: {str(e)}"
        )


@router.get("/trust-score/{campaign_id}")
async def get_trust_score(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Get existing trust score for a campaign"""
    
    trust_score = db.query(TrustScore).filter(
        TrustScore.campaign_id == campaign_id,
        TrustScore.organization_id == current_user["org_id"]
    ).first()
    
    if not trust_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trust score not calculated yet. Use POST /ml/trust-score/{campaign_id} to calculate."
        )
    
    return {
        "trust_score": float(trust_score.trust_score),
        "badge_level": trust_score.badge_level,
        "authenticity_score": trust_score.authenticity_score,
        "factual_accuracy_score": trust_score.factual_accuracy_score,
        "ai_text_probability": trust_score.ai_text_probability,
        "ai_image_probability": trust_score.ai_image_probability,
        "fact_check_results": trust_score.fact_check_results,
        "recommendations": trust_score.recommendations,
        "calculated_at": trust_score.calculated_at.isoformat()
    }
