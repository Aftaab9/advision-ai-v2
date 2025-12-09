from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from decimal import Decimal
from ..models import Campaign, Prediction, TrustScore


class AnalyticsService:
    """Service for analytics calculations"""
    
    @staticmethod
    def calculate_dashboard_stats(db: Session, org_id: str) -> Dict[str, Any]:
        """Calculate dashboard statistics"""
        
        campaigns = db.query(Campaign).filter(Campaign.organization_id == org_id).all()
        
        if not campaigns:
            return {
                "total_campaigns": 0,
                "total_spend": 0.0,
                "total_revenue": 0.0,
                "avg_ctr": 0.0,
                "avg_roi": 0.0,
                "avg_trust_score": 0.0,
                "platform_breakdown": {},
                "top_campaigns": []
            }
        
        # Calculate totals
        total_spend = sum(float(c.spend or 0) for c in campaigns)
        total_revenue = sum(float(c.revenue or 0) for c in campaigns)
        total_impressions = sum(c.impressions or 0 for c in campaigns)
        total_clicks = sum(c.clicks or 0 for c in campaigns)
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
        
        # Platform breakdown
        platform_breakdown = {}
        for campaign in campaigns:
            platform = campaign.platform
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    "count": 0,
                    "spend": 0.0,
                    "revenue": 0.0,
                    "impressions": 0,
                    "clicks": 0
                }
            
            platform_breakdown[platform]["count"] += 1
            platform_breakdown[platform]["spend"] += float(campaign.spend or 0)
            platform_breakdown[platform]["revenue"] += float(campaign.revenue or 0)
            platform_breakdown[platform]["impressions"] += campaign.impressions or 0
            platform_breakdown[platform]["clicks"] += campaign.clicks or 0
        
        # Calculate platform CTR and ROI
        for platform, data in platform_breakdown.items():
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["roi"] = ((data["revenue"] - data["spend"]) / data["spend"] * 100) if data["spend"] > 0 else 0
        
        # Get trust scores
        trust_scores = db.query(TrustScore).join(Campaign).filter(
            Campaign.organization_id == org_id
        ).all()
        
        avg_trust_score = sum(float(ts.trust_score) for ts in trust_scores) / len(trust_scores) if trust_scores else 0
        
        # Top campaigns by ROI
        campaigns_with_roi = [
            {
                "id": str(c.id),
                "name": c.name,
                "platform": c.platform,
                "roi": ((float(c.revenue or 0) - float(c.spend or 0)) / float(c.spend or 1)) * 100,
                "spend": float(c.spend or 0),
                "revenue": float(c.revenue or 0)
            }
            for c in campaigns if c.spend and c.revenue
        ]
        campaigns_with_roi.sort(key=lambda x: x["roi"], reverse=True)
        top_campaigns = campaigns_with_roi[:5]
        
        return {
            "total_campaigns": len(campaigns),
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "avg_ctr": round(avg_ctr, 2),
            "avg_roi": round(avg_roi, 2),
            "avg_trust_score": round(avg_trust_score, 2),
            "platform_breakdown": platform_breakdown,
            "top_campaigns": top_campaigns
        }
    
    @staticmethod
    def calculate_roi_metrics(campaign: Campaign) -> Dict[str, Any]:
        """Calculate ROI metrics for a campaign"""
        
        spend = float(campaign.spend or 0)
        revenue = float(campaign.revenue or 0)
        conversions = campaign.conversions or 0
        
        # ROI
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        
        # CAC (Customer Acquisition Cost)
        cac = spend / conversions if conversions > 0 else 0
        
        # CLV (Customer Lifetime Value) - simplified estimate
        clv = revenue / conversions if conversions > 0 else 0
        
        # Payback period (months) - simplified
        payback_period = (cac / (clv / 12)) if clv > 0 else 0
        
        return {
            "roi": round(roi, 2),
            "cac": round(cac, 2),
            "clv": round(clv, 2),
            "payback_period": round(payback_period, 2)
        }
