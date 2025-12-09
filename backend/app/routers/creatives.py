from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Creative
from ..services.storage import upload_file, delete_file
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


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_creative(
    campaign_id: UUID,
    file: UploadFile = File(...),
    ad_text: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Upload a creative (image) for a campaign"""
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Use JPEG, PNG, or GIF."
        )
    
    # Validate file size (10MB max)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit"
        )
    
    # Upload to R2
    try:
        image_url = await upload_file(file.file, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
    
    # Create creative record
    creative = Creative(
        organization_id=current_user["org_id"],
        campaign_id=campaign_id,
        ad_text=ad_text,
        image_url=image_url,
        creative_type="image",
        format="square"  # Default, can be detected
    )
    
    db.add(creative)
    db.commit()
    db.refresh(creative)
    
    # Analyze creative quality (async, don't wait)
    try:
        quality_result = await ml_client.analyze_creative_quality(image_url)
        # Store quality prediction
        from ..models import Prediction
        prediction = Prediction(
            organization_id=current_user["org_id"],
            campaign_id=campaign_id,
            creative_id=creative.id,
            prediction_type="quality",
            model_version="vit-v1",
            predictions=quality_result
        )
        db.add(prediction)
        db.commit()
    except Exception:
        pass  # Don't fail if ML service is down
    
    return {
        "id": str(creative.id),
        "image_url": image_url,
        "message": "Creative uploaded successfully"
    }


@router.get("/campaign/{campaign_id}")
async def list_campaign_creatives(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """List all creatives for a campaign"""
    
    creatives = db.query(Creative).filter(
        Creative.campaign_id == campaign_id,
        Creative.organization_id == current_user["org_id"]
    ).all()
    
    return [
        {
            "id": str(c.id),
            "ad_text": c.ad_text,
            "image_url": c.image_url,
            "creative_type": c.creative_type,
            "format": c.format,
            "created_at": c.created_at.isoformat()
        }
        for c in creatives
    ]


@router.delete("/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_creative(
    creative_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_data)
):
    """Delete a creative"""
    
    creative = db.query(Creative).filter(
        Creative.id == creative_id,
        Creative.organization_id == current_user["org_id"]
    ).first()
    
    if not creative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative not found"
        )
    
    # Delete from R2
    if creative.image_url:
        await delete_file(creative.image_url)
    
    db.delete(creative)
    db.commit()
    
    return None
