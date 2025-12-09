import httpx
from typing import Dict, Any
from ..config import settings


class MLClient:
    """Client for ML service communication"""
    
    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def predict_engagement(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement rate for campaign"""
        response = await self.client.post(
            f"{self.base_url}/predict/engagement",
            json=campaign_data
        )
        response.raise_for_status()
        return response.json()
    
    async def calculate_trust_score(self, campaign_id: str, text: str = None, image_url: str = None) -> Dict[str, Any]:
        """Calculate AI Justice Score (Trust Score)"""
        response = await self.client.post(
            f"{self.base_url}/trust/calculate",
            json={
                "campaign_id": campaign_id,
                "text": text,
                "image_url": image_url
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def analyze_creative_quality(self, image_url: str) -> Dict[str, Any]:
        """Analyze creative quality"""
        response = await self.client.post(
            f"{self.base_url}/creative/analyze",
            json={"image_url": image_url}
        )
        response.raise_for_status()
        return response.json()
    
    async def detect_ai_text(self, text: str) -> Dict[str, Any]:
        """Detect if text is AI-generated"""
        response = await self.client.post(
            f"{self.base_url}/detect/text",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    async def detect_ai_image(self, image_url: str) -> Dict[str, Any]:
        """Detect if image is AI-generated"""
        response = await self.client.post(
            f"{self.base_url}/detect/image",
            json={"image_url": image_url}
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        await self.client.aclose()


# Global ML client instance
ml_client = MLClient()
