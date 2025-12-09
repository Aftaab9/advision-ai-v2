from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import os
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user
from app.routers.documents import query_documents

router = APIRouter(prefix="/chat", tags=["chat"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


@router.post("/message")
async def chat_message(
    message: str,
    use_rag: bool = True,
    conversation_history: Optional[List[dict]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message to the AI chatbot with optional RAG context"""
    
    # Initialize conversation history
    if conversation_history is None:
        conversation_history = []
    
    # Build context from RAG if enabled
    context = ""
    relevant_docs = []
    
    if use_rag:
        # Query documents for relevant context
        rag_results = await query_documents(
            query=message,
            n_results=3,
            current_user=current_user
        )
        
        if rag_results["results"]:
            relevant_docs = rag_results["results"]
            context = "\n\n".join([
                f"[Document {i+1}]: {doc['content'][:500]}..."
                for i, doc in enumerate(relevant_docs)
            ])
    
    # Build system prompt
    system_prompt = """You are AdVision AI Assistant, an expert in marketing analytics and campaign optimization.
You help users understand their marketing data, provide insights, and answer questions about their campaigns.

Be concise, helpful, and data-driven in your responses. If you use information from documents, cite them."""
    
    if context:
        system_prompt += f"\n\nRelevant context from knowledge base:\n{context}"
    
    # Build messages for Groq
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for msg in conversation_history[-5:]:  # Last 5 messages for context
        messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Call Groq API
    if not GROQ_API_KEY:
        # Fallback response if no API key
        return {
            "response": "I'm AdVision AI Assistant. I can help you with marketing analytics, but I need a Groq API key to be configured. Please set GROQ_API_KEY environment variable.",
            "sources": relevant_docs,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-70b-versatile",  # Fast and capable
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            ai_response = result["choices"][0]["message"]["content"]
            
            return {
                "response": ai_response,
                "sources": relevant_docs,
                "timestamp": datetime.utcnow().isoformat(),
                "model": "llama-3.1-70b-versatile"
            }
    
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/quick-insights")
async def quick_insights(
    campaign_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quick AI insights about campaigns"""
    
    from app.models.campaign import Campaign
    
    # Get campaign data
    if campaign_id:
        campaign = db.query(Campaign).filter(
            Campaign.id == campaign_id,
            Campaign.organization_id == current_user.organization_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        prompt = f"""Analyze this campaign and provide 3 quick insights:
        
Campaign: {campaign.name}
Platform: {campaign.platform}
Budget: ₹{campaign.budget}
Spend: ₹{campaign.spend}
Revenue: ₹{campaign.revenue}
Impressions: {campaign.impressions}
Clicks: {campaign.clicks}
Conversions: {campaign.conversions}

Provide 3 actionable insights in bullet points."""
    
    else:
        # Get all campaigns
        campaigns = db.query(Campaign).filter(
            Campaign.organization_id == current_user.organization_id
        ).all()
        
        total_spend = sum(c.spend for c in campaigns)
        total_revenue = sum(c.revenue for c in campaigns)
        avg_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
        
        prompt = f"""Analyze this marketing portfolio and provide 3 quick insights:
        
Total Campaigns: {len(campaigns)}
Total Spend: ₹{total_spend}
Total Revenue: ₹{total_revenue}
Average ROI: {avg_roi:.1f}%

Provide 3 actionable insights in bullet points."""
    
    # Get AI response
    response = await chat_message(
        message=prompt,
        use_rag=False,
        current_user=current_user,
        db=db
    )
    
    return response
