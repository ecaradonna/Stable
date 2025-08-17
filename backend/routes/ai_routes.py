from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid
import json
from models.ai_models import (
    ChatMessage, ChatMessageCreate, ChatResponse,
    AIAlert, AIAlertCreate, AIAlertTrigger
)
from services.ai_service import StableYieldAI
from services.alert_service import AlertService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Initialize services
ai_service = StableYieldAI()
alert_service = AlertService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(message_data: ChatMessageCreate):
    """Send a message to StableYield AI and get response"""
    try:
        response = await ai_service.process_query(
            message=message_data.message,
            session_id=message_data.session_id
        )
        
        # In production, save to database
        # chat_record = ChatMessage(
        #     session_id=message_data.session_id,
        #     user_id=message_data.user_id,
        #     message=message_data.message,
        #     response=response.response
        # )
        # await db.chat_messages.insert_one(chat_record.dict())
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@router.get("/chat/samples")
async def get_sample_queries():
    """Get sample queries users can ask the AI"""
    return {
        "samples": ai_service.get_sample_queries(),
        "tips": [
            "Ask about specific stablecoins (USDT, USDC, DAI, etc.)",
            "Compare yields between different platforms",
            "Request data in table format for better readability",
            "Ask about risk factors and platform differences"
        ]
    }

@router.post("/alerts", response_model=AIAlert)
async def create_alert(alert_data: AIAlertCreate):
    """Create a new AI alert for yield thresholds"""
    try:
        alert = alert_service.create_alert(alert_data)
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/alerts/conditions")
async def get_alert_conditions():
    """Get available alert conditions and stablecoins"""
    return {
        "conditions": alert_service.get_alert_conditions(),
        "stablecoins": alert_service.get_available_stablecoins()
    }

@router.get("/alerts/{user_email}")
async def get_user_alerts(user_email: str):
    """Get all alerts for a specific user"""
    try:
        alerts = alert_service.get_user_alerts(user_email)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")

@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: str, user_email: str):
    """Delete a specific alert"""
    try:
        success = alert_service.delete_alert(alert_id, user_email)
        if success:
            return {"message": "Alert deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

@router.post("/alerts/check")
async def check_alerts():
    """Manually trigger alert checking (for testing)"""
    try:
        triggered_alerts = alert_service.check_alerts()
        return {
            "checked_at": datetime.utcnow().isoformat(),
            "triggered_count": len(triggered_alerts),
            "triggered_alerts": triggered_alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check alerts: {str(e)}")

# Import datetime for the endpoint
from datetime import datetime