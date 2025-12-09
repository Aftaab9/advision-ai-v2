from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os

app = FastAPI(
    title="AdVision AI - ML Service",
    description="Machine Learning inference service for marketing intelligence",
    version="1.0.0"
)


# Request/Response Models
class EngagementRequest(BaseModel):
    platform: str
    country: Optional[str] = None
    product_category: Optional[str] = None
    spend: float
    impressions: int
    reach: int


class TrustScoreRequest(BaseModel):
    campaign_id: str
    text: Optional[str] = None
    image_url: Optional[str] = None


class CreativeAnalysisRequest(BaseModel):
    image_url: str


class TextDetectionRequest(BaseModel):
    text: str


class ImageDetectionRequest(BaseModel):
    image_url: str


# Health check
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ml-service",
        "models_loaded": ["engagement-baseline", "trust-score-v1"]
    }


# Engagement Prediction
@app.post("/predict/engagement")
async def predict_engagement(request: EngagementRequest):
    """Predict engagement rate for a campaign"""
    
    # Simple baseline model (replace with actual ML model)
    # Formula: engagement_rate = (clicks / impressions) * platform_factor
    
    platform_factors = {
        "instagram": 1.2,
        "facebook": 1.0,
        "youtube": 0.8,
        "google_ads": 0.9,
        "twitter": 1.1,
        "linkedin": 0.7
    }
    
    platform_factor = platform_factors.get(request.platform.lower(), 1.0)
    
    # Estimate clicks based on spend and impressions
    estimated_ctr = 0.02 * platform_factor  # 2% base CTR
    estimated_clicks = int(request.impressions * estimated_ctr)
    
    # Calculate engagement rate
    engagement_rate = estimated_ctr
    
    return {
        "engagement_rate": round(engagement_rate, 4),
        "estimated_clicks": estimated_clicks,
        "confidence": 0.75,
        "model_version": "baseline-v1"
    }


# Trust Score Calculation
@app.post("/trust/calculate")
async def calculate_trust_score(request: TrustScoreRequest):
    """Calculate AI Justice Score (Trust Score)"""
    
    # Initialize scores
    authenticity_score = 1.0
    factual_accuracy_score = 1.0
    source_credibility_score = 1.0
    transparency_score = 1.0
    ethical_compliance_score = 1.0
    
    ai_text_probability = 0.0
    ai_image_probability = 0.0
    recommendations = []
    
    # AI Text Detection (simplified - replace with actual model)
    if request.text:
        # Simple heuristic: check for AI-like patterns
        text_lower = request.text.lower()
        ai_indicators = ["as an ai", "i'm an ai", "i cannot", "i don't have", "i'm not able"]
        
        if any(indicator in text_lower for indicator in ai_indicators):
            ai_text_probability = 0.9
            authenticity_score *= 0.7
            recommendations.append("Disclose AI-generated content")
        else:
            ai_text_probability = 0.1
    
    # AI Image Detection (simplified - replace with actual model)
    if request.image_url:
        # Placeholder: would use actual AI detection model
        ai_image_probability = 0.15  # Assume 15% chance
        if ai_image_probability > 0.5:
            authenticity_score *= 0.8
            recommendations.append("Verify image authenticity")
    
    # Fact-checking (simplified - would integrate with fact-check APIs)
    if request.text:
        # Placeholder for fact-checking
        factual_accuracy_score = 0.95
    
    # Calculate overall trust score (weighted average)
    trust_score = (
        authenticity_score * 0.30 +
        factual_accuracy_score * 0.25 +
        source_credibility_score * 0.20 +
        transparency_score * 0.15 +
        ethical_compliance_score * 0.10
    ) * 100
    
    # Determine badge level
    if trust_score >= 90:
        badge_level = "high"
    elif trust_score >= 70:
        badge_level = "medium"
    elif trust_score >= 50:
        badge_level = "low"
    else:
        badge_level = "risk"
    
    return {
        "trust_score": round(trust_score, 2),
        "badge_level": badge_level,
        "authenticity_score": round(authenticity_score, 2),
        "factual_accuracy_score": round(factual_accuracy_score, 2),
        "source_credibility_score": round(source_credibility_score, 2),
        "transparency_score": round(transparency_score, 2),
        "ethical_compliance_score": round(ethical_compliance_score, 2),
        "ai_text_probability": round(ai_text_probability, 2),
        "ai_image_probability": round(ai_image_probability, 2),
        "fact_check_results": [],
        "recommendations": recommendations
    }


# Creative Quality Analysis
@app.post("/creative/analyze")
async def analyze_creative(request: CreativeAnalysisRequest):
    """Analyze creative quality"""
    
    # Placeholder: would use Vision Transformer model
    quality_score = 75  # 0-100
    
    suggestions = []
    if quality_score < 50:
        suggestions.append("Increase image contrast")
        suggestions.append("Simplify text overlay")
    
    return {
        "quality_score": quality_score,
        "predicted_engagement": 0.035,
        "suggestions": suggestions,
        "model_version": "vit-v1"
    }


# AI Text Detection
@app.post("/detect/text")
async def detect_ai_text(request: TextDetectionRequest):
    """Detect if text is AI-generated"""
    
    # Simplified detection (replace with actual model like GPTZero)
    text_lower = request.text.lower()
    ai_indicators = ["as an ai", "i'm an ai", "i cannot", "i don't have"]
    
    ai_probability = 0.9 if any(ind in text_lower for ind in ai_indicators) else 0.1
    
    return {
        "ai_probability": ai_probability,
        "is_ai_generated": ai_probability > 0.5,
        "confidence": 0.75,
        "model_version": "roberta-v1"
    }


# AI Image Detection
@app.post("/detect/image")
async def detect_ai_image(request: ImageDetectionRequest):
    """Detect if image is AI-generated"""
    
    # Placeholder: would use actual AI image detection model
    ai_probability = 0.15
    
    return {
        "ai_probability": ai_probability,
        "is_ai_generated": ai_probability > 0.5,
        "confidence": 0.70,
        "model_version": "cnn-v1"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
